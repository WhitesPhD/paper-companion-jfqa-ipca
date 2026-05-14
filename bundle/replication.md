# Replication code (curated subset)

Foundational code from the paper's replication package on Harvard Dataverse.
Use these files to answer "how is X computed?" or "how is the estimator
implemented?" questions with the actual formula rather than a paraphrase.

The empirical scripts that reproduce each individual figure/table (one
`CODE/Figure_*.py` or `CODE/Table_*.py` per output) are not embedded — the
README at the bottom maps each one to its output, so you can still point the
reader at the right file on Dataverse when they ask.

---


## `replication/CODE/ipca_prop/ipca.py`

The IPCA estimator. The alternating least squares loop that iterates over $\Gamma$ and the latent factors $f_{t+1}$ lives here; use it to ground answers about the estimation mechanics.

```python
from sklearn.linear_model import ElasticNet
from joblib import Parallel, delayed
from numba import jit
import numpy as np
import scipy as sp
import progressbar
import warnings
import time
import re
from copy import deepcopy

class IPCARegressor:
    """
    This class implements the IPCA algorithm by Kelly, Pruitt, Su (2017).

    Parameters
    ----------

    n_factors : int, default=1
        The total number of factors to estimate. Note, the number of
        estimated factors is automatically reduced by the number of
        pre-specified factors. For example, if n_factors = 2 and one
        pre-specified factor is passed, then IPCARegressor will estimate
        one factor estimated in addition to the pre-specified factor.

    intercept : boolean, default=False
        Determines whether the model is estimated with or without an intercept

    max_iter : int, default=10000
        Maximum number of alternating least squares updates before the
        estimation is stopped

    iter_tol : float, default=10e-6
        Tolerance threshold for stopping the alternating least squares
        procedure
    """

    def __init__(self, n_factors=1, intercept=False, max_iter=10000,
                 iter_tol=10e-6):

        # paranoid parameter checking to make it easier for users to know when
        # they have gone awry and to make it safe to assume some variables can
        # only have certain settings
        if not isinstance(n_factors, int) or n_factors < 0:
            raise ValueError('n_factors must be an int greater / equal 1.')
        if not isinstance(intercept, bool):
            raise NotImplementedError('intercept must be  boolean')
        if not isinstance(iter_tol, float) or iter_tol >= 1:
            raise ValueError('Iteration tolerance must be smaller than 1.')

        # Save parameters to the object
        params = locals()
        for k, v in params.items():
            if k != 'self':
                setattr(self, k, v)


    def fit(self, Panel=None, PSF=None, refit=False, alpha=0., l1_ratio=1., **kwargs):
        """
        Fits the regressor to the data using an alternating least squares
        scheme.

        Parameters
        ----------
        Panel :  numpy array
            Panel of stacked data. Each row corresponds to an observation
            (i, t) where i denotes the entity index and t denotes
            the time index. The panel may be unbalanced. The number of unique
            entities is n_samples, the number of unique dates is T, and
            the number of characteristics used as instruments is L.
            The columns of the panel are organized in the following order:

            - Column 1: entity id (i)
            - Column 2: time index (t)
            - Column 3: dependent variable corresponding to observation (i,t)
            - Column 4 to column 4+L: characteristics.

        PSF : numpy array, optional
            Set of pre-specified factors as matrix of dimension (M, T)

        refit : boolean, optional
            Indicates whether the regressor should be re-fit. If set to True
            the function will skip unpacking the panel into a tensor and
            instead use the stored values from the previous fit. Note, it is
            still necessary to pass the previously used P.

        alpha : scalar
            Regularizing constant for Gamma estimation.  If this is set to
            zero then the estimation defaults to non-regularized.

        l1_ratio : scalar
            Ratio of l1 and l2 penalties for elastic net Gamma fit.

        Returns
        -------

        Gamma : numpy array
            Array with dimensions (L, n_factors) containing the
            mapping between characteristics and factors loadings. If there
            are M many pre-specified factors in the model then the
            matrix returned is of dimension (L, (n_factors+M)).
            If an intercept is included in the model, its loadings are
            returned in the last column of Gamma.

        Factors : numpy array
            Array with dimensions (n_factors, T) containing the estimated
            factors. If pre-specified factors were passed the returned
            array is of dimension ((n_factors - M), T),
            corresponding to the n_factors - M many factors estimated on
            top of the pre-specified ones.

        """
        # Check re-fitting is valid
        if refit:
            try:
                self.X
            except AttributeError:
                raise ValueError('Refit only possible after initial fit.')

        # Check panel input
        if Panel is None:
            raise ValueError('Must pass panel input data.')
        else:
            # remove panel rows containing missing obs
            Panel = Panel[~np.any(np.isnan(Panel), axis=1)]

        # Unpack the Panel
        if not refit:
            X, W, val_obs = self._unpack_panel(Panel)
        else:
            Panel, X, W, val_obs = self.Panel, self.X, self.W, self.val_obs

        # Handle pre-specified factors
        if PSF is not None:
            if np.size(PSF, axis=1) != np.size(np.unique(Panel[:, 1])):
                raise ValueError("""Number of PSF observations must match
                                 number of unique dates in panel P""")
            self.has_PSF = True
            self.n_PSF = np.size(PSF, axis=0)
        else:
            self.has_PSF = False

        if self.has_PSF:
            if np.size(PSF, axis=0) == self.n_factors:
                print("""Note: The number of factors (n_factors) to be
                      estimated matches the number of
                      pre-specified factors. No additional factors
                      will be estimated. To estimate additional
                      factors increase n_factors.""")

        #  Treating intercept as if was a prespecified factor
        if self.intercept:
            self.n_factors_eff = self.n_factors + 1
            if PSF is not None:
                PSF = np.concatenate((PSF, np.ones((1, self.T))), axis=0)
            elif PSF is None:
                PSF = np.ones((1, self.T))
        else:
            self.n_factors_eff = self.n_factors

        # Check that enough features provided
        if np.size(Panel, axis=1) < 4:
            raise ValueError("""Must provide at least one characteristic or constant""")

        # Determine fit case - if intercept or PSF or both use PSFcase fitting
        # Note PSFcase in contrast to has_PSF is only indicating
        # that the IPCA fitting is carried out as if PSF were passed even if
        # only an intercept was passed.
        self.PSFcase = True if self.has_PSF or self.intercept else False

        # Run IPCA
        Gamma, Factors = self._fit_ipca(X, W, val_obs, Panel=Panel, PSF=PSF, **kwargs)

        # Store estimates
        if self.PSFcase:
            if self.intercept and self.has_PSF:
                # PSF = np.concatenate((PSF, np.ones((1, len(self.dates)))), axis=0)
                PSF = PSF
            elif self.intercept:
                PSF = np.ones((1, len(self.dates)))
            if Factors is not None:
                Factors = np.concatenate((Factors, PSF), axis=0)
            else:
                Factors = PSF

        self.Gamma_Est, self.Factors_Est = Gamma, Factors

        # Save unpacked panel for Re-fitting
        if not refit:
            self.Panel = Panel
            self.PSF = PSF
            self.X = X
            self.W = W
            self.val_obs = val_obs

        # Compute Goodness of Fit
        self.r2_total, self.r2_pred, self.r2_total_x, self.r2_pred_x = \
            self._R2_comps(Panel=Panel)

        return self.Gamma_Est, self.Factors_Est


    def predict(self, Panel=None, mean_factor=False, cond_mean_factor=False):
        """
        Predicts fitted values for a previously fitted regressor

        Parameters
        ----------
        Panel :  numpy array
            Panel of stacked data. Each row corresponds to an observation
            (i, t) where i denotes the entity index and t denotes
            the time index. The panel may be unbalanced. If an observation
            contains missing data NaN will be returned. Note that the
            number of passed characteristics L must match the
            number of characteristics used when fitting the regressor.
            The columns of the panel are organized in the following order:

            - Column 1: entity id (i)
            - Column 2: time index (t)
            - Column 3 to column 3+L: characteristics.

        mean_factor: boolean
            If true, the estimated factors are averaged in the time-series
            before prediction.


        Returns
        -------

        Ypred : numpy array
            The length of the returned array matches the
            the length of data. A nan will be returned if there is missing
            characteristics information.
        """

        if Panel is None:
            raise ValueError("""A panel of characteristics data must be
                              provided.""")

        if np.any(np.isnan(Panel)):
            raise ValueError("""Cannot contain missing observations / nan
                              values.""")
        N = np.size(Panel, axis=0)
        Ypred = np.full((N), np.nan)

        mean_Factors_Est = np.mean(self.Factors_Est, axis=1).reshape((-1, 1))
        if mean_factor:
            Ypred[:] = np.squeeze(Panel[:, 2:].dot(self.Gamma_Est)\
                .dot(mean_Factors_Est))

        elif cond_mean_factor:
            for t_i, t in enumerate(self.dates):
                if t_i < 12*2:
                    cond_mean_Factors_Est = np.mean(self.Factors_Est[:, :t_i+1], axis=1).reshape((-1, 1))
                else:
                    cond_mean_Factors_Est = np.mean(self.Factors_Est[:, t_i-12*2:t_i+1], axis=1).reshape((-1, 1))
                ix = (Panel[:, 1] == t)
                Ypred[ix] = np.squeeze(Panel[ix, 2:].dot(self.Gamma_Est)\
                    .dot(cond_mean_Factors_Est))

        else:
            for t_i, t in enumerate(self.dates):
                ix = (Panel[:, 1] == t)
                Ypred[ix] = np.squeeze(Panel[ix, 2:].dot(self.Gamma_Est)\
                    .dot(self.Factors_Est[:, t_i]))

        return Ypred
    

    def predict_bf(self, Panel=None):
        """
        Predicts fitted values for a previously fitted regressor only of beta*factor component

        Parameters
        ----------
        Panel :  numpy array
            Panel of stacked data. Each row corresponds to an observation
            (i, t) where i denotes the entity index and t denotes
            the time index. The panel may be unbalanced. If an observation
            contains missing data NaN will be returned. Note that the
            number of passed characteristics L must match the
            number of characteristics used when fitting the regressor.
            The columns of the panel are organized in the following order:

            - Column 1: entity id (i)
            - Column 2: time index (t)
            - Column 3 to column 3+L: characteristics.

        mean_factor: boolean
            If true, the estimated factors are averaged in the time-series
            before prediction.


        Returns
        -------

        Ypred : numpy array
            The length of the returned array matches the
            the length of data. A nan will be returned if there is missing
            characteristics information.
        """

        if Panel is None:
            raise ValueError("""A panel of characteristics data must be
                              provided.""")

        if np.any(np.isnan(Panel)):
            raise ValueError("""Cannot contain missing observations / nan
                              values.""")
        N = np.size(Panel, axis=0)
        Ypred = np.full((N), np.nan)

        if self.intercept:
            for t_i, t in enumerate(self.dates):
                ix = (Panel[:, 1] == t)
                Ypred[ix] = np.squeeze(Panel[ix, 2:].dot(self.Gamma_Est[:, :-1])\
                    .dot(self.Factors_Est[:-1, t_i]))
        else:
            for t_i, t in enumerate(self.dates):
                ix = (Panel[:, 1] == t)
                Ypred[ix] = np.squeeze(Panel[ix, 2:].dot(self.Gamma_Est)\
                    .dot(self.Factors_Est[:, t_i]))

        return Ypred

    def predict_alpha(self, Panel=None):
        """
        Predicts fitted values for a previously fitted regressor only of beta*factor component

        Parameters
        ----------
        Panel :  numpy array
            Panel of stacked data. Each row corresponds to an observation
            (i, t) where i denotes the entity index and t denotes
            the time index. The panel may be unbalanced. If an observation
            contains missing data NaN will be returned. Note that the
            number of passed characteristics L must match the
            number of characteristics used when fitting the regressor.
            The columns of the panel are organized in the following order:

            - Column 1: entity id (i)
            - Column 2: time index (t)
            - Column 3 to column 3+L: characteristics.

        mean_factor: boolean
            If true, the estimated factors are averaged in the time-series
            before prediction.


        Returns
        -------

        Ypred : numpy array
            The length of the returned array matches the
            the length of data. A nan will be returned if there is missing
            characteristics information.
        """

        if Panel is None:
            raise ValueError("""A panel of characteristics data must be
                              provided.""")

        if np.any(np.isnan(Panel)):
            raise ValueError("""Cannot contain missing observations / nan
                              values.""")

        if self.intercept is False:
            raise ValueError("Requires fitting a model with intercept first.")


        N = np.size(Panel, axis=0)
        Ypred = np.full((N), np.nan)


        for t_i, t in enumerate(self.dates):
            ix = (Panel[:, 1] == t)
            Ypred[ix] = np.squeeze(Panel[ix, 2:].dot(self.Gamma_Est[:, -1])\
                .dot(self.Factors_Est[-1, t_i]))

        return Ypred


    def BS_Walpha(self, ndraws=1000, blocksize=1, n_jobs=1, backend='loky'):
        """
        Bootstrap inference on the hypothesis Gamma_alpha = 0

        Parameters
        ----------

        ndraws  : integer, default=1000
            Number of bootstrap draws and re-estimations to be performed

        backend : optional
            Value is either 'loky' or 'multiprocessing'

        n_jobs  : integer
            Number of workers to be used. If -1, all available workers are
            used.

        Returns
        -------

        pval : float
            P-value from the hypothesis test H0: Gamma_alpha=0
        """

        if not self.intercept:
            raise ValueError('Need to fit model with intercept first.')

        # Compute Walpha
        Walpha = self.Gamma_Est[:, -1].T.dot(self.Gamma_Est[:, -1])

        # Compute residuals
        d = np.full((self.L, self.T), np.nan)

        for t_i in range(self.T):
            d[:, t_i] = self.X[:, t_i]-self.W[:, :, t_i].dot(self.Gamma_Est)\
                .dot(self.Factors_Est[:, t_i])

        print("Starting Bootstrap...")
        Walpha_b = Parallel(n_jobs=n_jobs, backend=backend, verbose=20)(
            delayed(_BS_Walpha_sub_block)(self, n, d, blocksize) for n in range(ndraws))
        print("Done!")

        print(Walpha_b, Walpha)
        pval = np.sum(Walpha_b > Walpha)/ndraws
        return Walpha_b, Walpha, pval
        # return pval

    def BS_Walpha_group(self, ndraws=1000, blocksize=1, n_jobs=1, alpha_index = 0, backend='loky'):
        """
        Bootstrap inference on the hypothesis Gamma_alpha = 0

        Parameters
        ----------

        ndraws  : integer, default=1000
            Number of bootstrap draws and re-estimations to be performed

        backend : optional
            Value is either 'loky' or 'multiprocessing'

        n_jobs  : integer
            Number of workers to be used. If -1, all available workers are
            used.

        Returns
        -------

        pval : float
            P-value from the hypothesis test H0: Gamma_alpha=0
        """

        if not self.intercept:
            raise ValueError('Need to fit model with intercept first.')

        # Compute Walpha
        Walpha = self.Gamma_Est[alpha_index, -1].T.dot(self.Gamma_Est[alpha_index, -1])

        # Compute residuals
        d = np.full((self.L, self.T), np.nan)

        for t_i in range(self.T):
            d[:, t_i] = self.X[:, t_i]-self.W[:, :, t_i].dot(self.Gamma_Est)\
                .dot(self.Factors_Est[:, t_i])

        print("Starting Bootstrap...")
        Walpha_b = Parallel(n_jobs=n_jobs, backend=backend, verbose=20)(
            delayed(_BS_Walpha_sub_block_group)(self, n, d, blocksize, alpha_index) for n in range(ndraws))
        print("Done!")

        print(Walpha_b, Walpha)
        pval = np.sum(Walpha_b > Walpha)/ndraws
        return Walpha_b, Walpha, pval
        # return pval

    def BS_Wbeta(self, l, component=None, ndraws=1000, blocksize=1, n_jobs=1, backend='loky'):
        """
        Test of instrument significance.
        Bootstrap inference on the hypothesis  l-th column of Gamma_beta = 0.

        Parameters
        ----------

        l   : integer
            Position of the characteristics for which the bootstrap is to be
            carried out. For example, if there are 10 characteristics, l is in
            the range 0 to 9 (left-/right-inclusive).

        ndraws  : integer, default=1000
            Number of bootstrap draws and re-estimations to be performed

        n_jobs  : integer
            Number of workers to be used for multiprocessing.
            If -1, all available Workers are used.

        backend : optional

        Returns
        -------

        pval : float
            P-value from the hypothesis test H0: Gamma_alpha=0
        """

        # if self.PSFcase:
        #     raise ValueError('Need to fit model without intercept first.')


        if component is None:
            raise ValueError("Need to choose one of 'total', 'factor_x' where x=1,2,...")
        elif component == 'total':
            gamma_pos = slice(0,None,None)
        elif re.match('^intercept_[0-9]+', component):
            gamma_pos = slice(int(component[component.find('_')+1:]))
        elif re.match('^factor_[0-9]+', component):
            gamma_pos = int(component[component.find('_')+1:])-1
        else:
            raise ValueError("component needs to be one of 'total', 'factor_x' where x=1,2,...")

        print("Running component: ", component)

        # Compute Wbeta_l if l-th characteristics is set to zero
        Wbeta_l = np.squeeze(self.Gamma_Est[l, gamma_pos].reshape((1, -1)).dot(self.Gamma_Est[l, gamma_pos].reshape((1, -1)).T))

        # Wbeta_l = np.trace(Wbeta_l)
        # Compute residuals
        d = np.full((self.L, self.T), np.nan)
        for t_i, t in enumerate(self.dates):
            d[:, t_i] = self.X[:, t_i]-self.W[:, :, t_i].dot(self.Gamma_Est)\
                .dot(self.Factors_Est[:, t_i])

        print("Starting Bootstrap...")
        Wbeta_l_b = Parallel(n_jobs=n_jobs, backend=backend, verbose=10)(
            delayed(_BS_Wbeta_sub_block)(self, n, d, l, gamma_pos, blocksize) for n in range(ndraws))
        print("Done!")

        pval = np.sum(Wbeta_l_b > Wbeta_l)/ndraws
        print(Wbeta_l_b, Wbeta_l)

        return Wbeta_l_b, Wbeta_l, pval
        # return pval

    def BS_Wdelta(self, ndraws=1000, l_delta = 1, blocksize=1, n_jobs=1, backend='loky'):
        """
        Bootstrap inference on the hypothesis Gamma_delta = 0

        Parameters
        ----------

        ndraws  : integer, default=1000
            Number of bootstrap draws and re-estimations to be performed

        backend : optional
            Value is either 'loky' or 'multiprocessing'

        n_jobs  : integer
            Number of workers to be used. If -1, all available workers are
            used.

        Returns
        -------

        pval : float
            P-value from the hypothesis test H0: Gamma_alpha=0
        """

        # if self.intercept:
        #     raise ValueError('Need to fit model without intercept first.')
        # if not self.has_PSF:
        #     raise ValueError('Need to fit model with pre-specified factors first.')

        L, Ktilde = np.shape(self.Gamma_Est)
        K_PSF, _ = np.shape(self.PSF)
        K = Ktilde - K_PSF - l_delta + 1

        # Compute Wdelta
        Wdelta = (self.Gamma_Est[:, -l_delta].reshape((-1, 1), order="F")).T.dot(self.Gamma_Est[:, -l_delta].reshape((-1, 1), order="F"))
        Wdelta = np.squeeze(Wdelta)

        # Compute residuals
        d = np.full((self.L, self.T), np.nan)

        for t_i, t in enumerate(self.dates):
            d[:, t_i] = self.X[:, t_i]-self.W[:, :, t_i].dot(self.Gamma_Est)\
                .dot(self.Factors_Est[:, t_i])

        print("Starting Bootstrap...")
        Wdelta_b = Parallel(n_jobs=n_jobs, backend=backend, verbose=20)(
            delayed(_BS_Wdelta_sub_block)(self, n, d, l_delta, blocksize) for n in range(ndraws))
        print("Done!")

        print(Wdelta_b, Wdelta)
        pval = np.sum(Wdelta_b > Wdelta)/ndraws
        return pval
    

    def predictOOS(self, Panel=None, mean_factor=False):
        """
        Predicts time t+1 observation using an out-of-sample design.

        Parameters
        ----------
        Panel :  numpy array
            Panel of stacked data. Each row corresponds to an observation
            (i,t) where i denotes the entity index and t denotes
            the time index. All data must correspond to time t, i.e. all
            observations occur on the same date.
            If an observation contains missing data NaN will be returned.
            Note that the number of characteristics (L) passed,
            has to match the number of characteristics used when fitting
            the regressor.
            The columns of the panel are organized in the following order:

            - Column 1: entity id (i)
            - Column 2: time index (t)
            - Column 3: dependent variable corresponding to observation (i,t)
            - Column 4 to column 4+L: characteristics.

        mean_factor: boolean
            If true, the estimated factors are averaged in the time-series
            before prediction.


        Returns
        -------

        Ypred : numpy array
            The length of the returned array matches the
            the length of data. A nan will be returned if there is missing
            characteristics information.
        """

        if Panel is None:
            raise ValueError("""A panel of characteristics data must be
                              provided.""")

        if len(np.unique(Panel[:, 1])) > 1:
            raise ValueError('The panel must only have a single timestamp.')

        N = np.size(Panel, axis=0)
        Ypred = np.full((N), np.nan)

        # Unpack the panel into Z, Y
        Z, Y = Panel[:, 3:], Panel[:, 2]

        # Compute realized factor returns
        Numer = self.Gamma_Est.T.dot(Z.T).dot(Y)
        Denom = self.Gamma_Est.T.dot(Z.T).dot(Z).dot(self.Gamma_Est)
        Factor_OOS = np.linalg.solve(Denom, Numer.reshape((-1, 1)))

        if mean_factor:
            Ypred = np.squeeze(Z.dot(self.Gamma_Est)\
                    .dot(np.mean(self.Factors_Est, axis=1).reshape((-1, 1))))
        else:
            Ypred = Z.dot(self.Gamma_Est).dot(Factor_OOS)

        return Ypred


    def _unpack_panel(self, Panel):
        """ Converts a stacked panel of data where each row corresponds to an
        observation (i, t) into a tensor of dimensions (N, L, T) where N is the
        number of unique entities, L is the number of characteristics and T is
        the number of unique dates

        Parameters
        ----------

        Panel : Panel of data. Each row corresponds to an observation (i, t).
                The columns are ordered in the following manner:
                COLUMN 1: entity id (i)
                COLUMN 2: time index (t)
                COLUMN 3: depdent variable Y(i,t)
                COLUMN 4 and following: L characteristics

        Returns
        -------
        X: array-like
            matrix of dimensions (L, T), containing the characteristics
            weighted portfolios

        W: array-like
            matrix of dimension (L, L, T)

        val_obs: array-like
            matrix of dimension (T), containting the number of non missing
            observations at each point in time
        """

        dates = np.unique(Panel[:, 1])
        ids = np.unique(Panel[:, 0])
        T = np.size(dates, axis=0)
        N = np.size(ids, axis=0)
        L = np.size(Panel, axis=1) - 3
        print('The panel dimensions are:')
        print('n_samples:', N, ', L:', L, ', T:', T)

        bar = progressbar.ProgressBar(maxval=T,
                                      widgets=[progressbar.Bar('=', '[', ']'),
                                               ' ', progressbar.Percentage()])
        bar.start()
        X = np.full((L, T), np.nan)
        W = np.full((L, L, T), np.nan)
        val_obs = np.full((T), np.nan)
        for t_i, t in enumerate(dates):
            ixt = (Panel[:, 1] == t)
            val_obs[t_i] = np.sum(ixt)
            # Define characteristics weighted matrices
            X[:, t_i] = Panel[ixt, 3:].T.dot(Panel[ixt, 2])/val_obs[t_i]
            W[:, :, t_i] = Panel[ixt, 3:].T.dot(Panel[ixt, 3:])/val_obs[t_i]
            bar.update(t_i)
        bar.finish()

        # Store panel dimensions
        self.ids, self.dates, self.T, self.N, self.L = ids, dates, T, N, L

        return X, W, val_obs


    def _fit_ipca(self, X, W, val_obs, Panel=None, PSF=None, quiet=False, **kwargs):
        """
        Fits the regressor to the data using alternating least squares

        Parameters
        ----------
        X : array-like of shape (L, T),
            i.e. characteristics weighted portfolios

        W : array_like of shape (L, L, T),

        val_obs: array-like
            matrix of dimension (T), containting the number of non missing
            observations at each point in time

        Panel : optional, Panel of data.

                Each row corresponds to an observation (i, t).
                The columns are ordered in the following manner:
                COLUMN 1: entity id (i)
                COLUMN 2: time index (t)
                COLUMN 3: depdent variable Y(i,t)
                COLUMN 4 and following: L characteristics

        PSF : optional, array-like of shape (M, T), i.e.
            pre-specified factors

        quiet   : optional, bool
            If true no text output will be produced

        Returns
        -------
        Gamma : array-like with dimensions (L, n_factors). If there
            are n_prespec many pre-specified factors in the model then the
            matrix returned is of dimension (L, (n_factors+M)).
            If an intercept is included in the model, its loadings are returned
            in the last column of Gamma.

        Factors : array_like with dimensions (n_factors, T). If
            pre-specified factors were passed the returned matrix is
            of dimension ((n_factors - M), T), corresponding to the
            n_factors - M many factors estimated on top of the pre-
            specified ones.
        """

        # Initialize the Alternating Least Squares Procedure
        Gamma_Old, s, v = np.linalg.svd(X)
        Gamma_Old = Gamma_Old[:, :self.n_factors_eff]
        s = s[:self.n_factors_eff]
        v = v[:self.n_factors_eff, :]
        Factor_Old = np.diag(s).dot(v)

        # Estimation Step
        tol_current = 1

        iter = 0

        while((iter <= self.max_iter) and (tol_current > self.iter_tol)):

            Gamma_New, Factor_New = self._ALS_fit(Gamma_Old, W, X, val_obs, Panel=Panel, PSF=PSF, **kwargs)
            if self.PSFcase:
                tol_current = np.max(np.abs(Gamma_New - Gamma_Old))
            else:
                tol_current_G = np.max(np.abs(Gamma_New - Gamma_Old))
                tol_current_F = np.max(np.abs(Factor_New - Factor_Old))
                tol_current = max(tol_current_G, tol_current_F)

            # Update factors and loadings
            Factor_Old, Gamma_Old = Factor_New, Gamma_New

            iter += 1
            if not quiet:
                print('Step', iter, '- Aggregate Update:', tol_current)

        if not quiet:
            print('-- Convergence Reached --')

        return Gamma_New, Factor_New


    def _ALS_fit(self, Gamma_Old, W, X, val_obs, Panel=None, PSF=None,
                 n_jobs=1, backend="loky", **kwargs):
        """Alternating least squares procedure to fit params

        The alternating least squares procedure switches back and forth
        between evaluating the first order conditions for Gamma_Beta, and the
        factors until convergence is reached. This function carries out one
        complete update procedure and will need to be called repeatedly using
        the updated Gamma's and factors as inputs.
        """

        T = self.T

        if PSF is None:
            L, K = np.shape(Gamma_Old)
            Ktilde = K
        else:
            L, Ktilde = np.shape(Gamma_Old)
            K_PSF, _ = np.shape(PSF)
            K = Ktilde - K_PSF

        # ALS Step 1
        if K > 0:

            # case with no observed factors
            if PSF is None:
                if n_jobs > 1:
                    F_New = Parallel(n_jobs=n_jobs, backend=backend)(
                                delayed(_Ft_fit)(
                                    Gamma_Old, W[:,:,t], X[:,t])
                                for t in range(T))
                    F_New = np.stack(F_New, axis=1)

                else:
                    F_New = np.full((K, T), np.nan)
                    for t in range(T):
                        F_New[:,t] = _Ft_fit(Gamma_Old, W[:,:,t], X[:,t])

            # observed factors+latent factors case
            else:
                if n_jobs > 1:
                    F_New = Parallel(n_jobs=n_jobs, backend=backend)(
                                delayed(_Ft_PSF_fit)(
                                    Gamma_Old, W[:,:,t], X[:,t], PSF[:,t],
                                    K, Ktilde)
                                for t in range(T))
                    F_New = np.stack(F_New, axis=1)

                else:
                    F_New = np.full((K, T), np.nan)
                    for t in range(T):
                        F_New[:,t] = _Ft_PSF_fit(Gamma_Old, W[:,:,t], X[:,t],
                                                 PSF[:,t], K, Ktilde)

        else:
            F_New = None

        # ALS Step 2
        Gamma_New = _Gamma_portfolio_fit(F_New, X, W, val_obs, PSF, L, K,
                                         Ktilde, T)


        # Enforce Orthogonality of Gamma_Alpha and Gamma_beta
        if PSF is not None and K>0:
            regbeta = np.linalg.lstsq(Gamma_New[:, :K], Gamma_New[:, K:])
            regbeta = regbeta[0]
            Gamma_New[:, K:] = Gamma_New[:, K:]-Gamma_New[:, :K].dot(regbeta)
            F_New += regbeta.dot(PSF)


        # Enforce Orthogonality of Gamma_Beta and factors F
        if K > 0:
            R1 = _numba_chol(Gamma_New[:, :K].T.dot(Gamma_New[:, :K])).T
            R2, _, _ = _numba_svd(R1.dot(F_New).dot(F_New.T).dot(R1.T))
            Gamma_New[:, :K] = _numba_lstsq(Gamma_New[:, :K].T,
                                            R1.T)[0].dot(R2)
            F_New = _numba_solve(R2, R1.dot(F_New))


        # Enforce sign convention for Gamma_Beta and F_New
        if K > 0:
            sg = np.sign(np.mean(F_New, axis=1)).reshape((-1, 1))
            sg[sg == 0] = 1
            Gamma_New[:, :K] = np.multiply(Gamma_New[:, :K], sg.T)
            F_New = np.multiply(F_New, sg)

        return Gamma_New, F_New


    def _R2_comps(self, Panel=None):
        """
        Computes the goodness of fit measures both at the entity level
        and at the managed portfolio level. Requires the estimator to be
        fitted previously.

        Parameters
        ----------
        Panel   :   Panel of stacked data. Each row corresponds to an
                    observation (i, t) where i denotes the entity index and t
                    denotes the time index. The panel may be unbalanced. The
                    number of unique entities is n_samples, the number of
                    unique dates is T, and the number of characteristics used
                    as instruments is L. The columns of the panel are
                    organized in the following order:

                - Column 1: entity id (i)
                - Column 2: time index (t)
                - Column 3: dependent variable corresponding to observation
                            (i,t)
                - Column 4 to column 4+L: characteristics.

        """

        # Compute goodness of fit measures, entity level
        Ytrue = Panel[:, 2]

        # R2 Total
        Ypred = self.predict(np.delete(Panel, 2, axis=1), mean_factor=False)
        r2_total = 1-np.nansum((Ypred-Ytrue)**2)/np.nansum(Ytrue**2)

        # R2 Pred
        Ypred = self.predict(np.delete(Panel, 2, axis=1), mean_factor=True)
        r2_pred = 1-np.nansum((Ypred-Ytrue)**2)/np.nansum(Ytrue**2)


        # Compute goodness of fit measures, portfolio level
        Num_tot, Denom_tot = 0, 0
        Num_pred, Denom_pred = 0, 0

        mean_Factors_Est = np.mean(self.Factors_Est, axis=1).reshape((-1, 1))

        for t_i, t in enumerate(self.dates):
            Ytrue = self.X[:, t_i]
            # R2 Total
            Ypred = self.W[:, :, t_i].dot(self.Gamma_Est)\
                .dot(self.Factors_Est[:, t_i])
            Num_tot += (Ytrue-Ypred).T.dot((Ytrue-Ypred))
            Denom_tot += Ytrue.T.dot(Ytrue)

            # R2 Pred
            Ypred = self.W[:, :, t_i].dot(self.Gamma_Est).dot(mean_Factors_Est)
            Ypred = np.squeeze(Ypred)
            Num_pred += (Ytrue-Ypred).T.dot((Ytrue-Ypred))
            Denom_pred += Ytrue.T.dot(Ytrue)
            

        r2_total_x = 1-Num_tot/Denom_tot
        r2_pred_x = 1-Num_pred/Denom_pred

        return r2_total, r2_pred, r2_total_x, r2_pred_x





def _Ft_fit(Gamma_Old, W_t, X_t):
    """helper func to parallelize F ALS fit"""

    m1 = Gamma_Old.T.dot(W_t).dot(Gamma_Old)
    m2 = Gamma_Old.T.dot(X_t)

    return np.squeeze(_numba_solve(m1, m2.reshape((-1, 1))))


def _Ft_PSF_fit(Gamma_Old, W_t, X_t, PSF_t, K, Ktilde):
    """helper func to parallelize F ALS fit with observed factors"""

    m1 = Gamma_Old[:,:K].T.dot(W_t).dot(Gamma_Old[:,:K])
    m2 = Gamma_Old[:,:K].T.dot(X_t)
    m2 -= Gamma_Old[:,:K].T.dot(W_t).dot(Gamma_Old[:,K:Ktilde]).dot(PSF_t)

    return np.squeeze(_numba_solve(m1, m2.reshape((-1, 1))))


def _Gamma_portfolio_fit(F_New, X, W, val_obs, PSF, L, K, Ktilde, T):
    """helper function for fitting gamma without panel"""

    Numer = _numba_full((L*Ktilde, 1), 0.0)
    Denom = _numba_full((L*Ktilde, L*Ktilde), 0.0)

    # no observed factors
    if PSF is None:
        for t in range(T):

            Numer += _numba_kron(X[:, t].reshape((-1, 1)),
                                 F_New[:, t].reshape((-1, 1)))\
                                 * val_obs[t]
            Denom += _numba_kron(W[:, :, t],
                                 F_New[:, t].reshape((-1, 1))
                                 .dot(F_New[:, t].reshape((1, -1)))) \
                                 * val_obs[t]

    # observed+latent factors
    elif K > 0:
        for t in range(T):
            Numer += _numba_kron(X[:, t].reshape((-1, 1)),
                                 np.vstack(
                                 (F_New[:, t].reshape((-1, 1)),
                                 PSF[:, t].reshape((-1, 1)))))\
                                 * val_obs[t]
            Denom_temp = np.vstack((F_New[:, t].reshape((-1, 1)),
                                   PSF[:, t].reshape((-1, 1))))
            Denom += _numba_kron(W[:, :, t], Denom_temp.dot(Denom_temp.T)
                                 * val_obs[t])

    # only observed factors
    else:
        for t in range(T):
            Numer += _numba_kron(X[:, t].reshape((-1, 1)),
                                 PSF[:, t].reshape((-1, 1)))\
                                 * val_obs[t]
            Denom += _numba_kron(W[:, :, t],
                                 PSF[:, t].reshape((-1, 1))
                                 .dot(PSF[:, t].reshape((-1, 1)).T))\
                                 * val_obs[t]

    Gamma_New = _numba_solve(Denom, Numer).reshape((L, Ktilde))

    return Gamma_New


def _Gamma_panel_fit(F_New, Panel, PSF, L, Ktilde, alpha, l1_ratio, **kwargs):
    """helper function for estimating vectorized Gamma with panel"""

    # join observed factors with latent factors and map to panel
    if PSF is None:
        F = F_New
    else:
        if F_New is None:
            F = PSF
        else:
            F = np.vstack((F_New, PSF))
    F = F[:,np.unique(Panel[:,1], return_inverse=True)[1]]

    # interact factors and characteristics
    ZkF = np.hstack((F[k,:,None] * Panel[:,3:] for k in range(Ktilde)))

    # elastic net fit
    if alpha:
        mod = ElasticNet(alpha=alpha, l1_ratio=l1_ratio, **kwargs)
        mod.fit(ZkF, Panel[:,2])
        gamma = mod.coef_

    # OLS fit
    else:
        gamma = _numba_lstsq(ZkF, Panel[:,2])[0]

    gamma = gamma.reshape((Ktilde, L)).T

    return gamma


def _BS_Walpha_sub(model, n, d):
    X_b = np.full((model.L, model.T), np.nan)
    np.random.seed(n)
    Gamma = None
    # Re-estimate unrestricted model
    while Gamma is None:
        try:
            for t in range(model.T):
                dof = 5
                tvar = dof / (dof-2)
                tstudent = (1/np.sqrt(tvar))*np.random.standard_t(dof)
                d_temp = tstudent*d[:,np.random.randint(0,high=model.T)]
                X_b[:, t] = model.W[:, :, t].dot(model.Gamma_Est[:, :-1])\
                    .dot(model.Factors_Est[:-1, t]) + d_temp

            Gamma, Factors = model._fit_ipca(X=X_b, W=model.W, val_obs=model.val_obs,
                                              PSF=model.PSF, quiet=True)

        except np.linalg.LinAlgError:
            warnings.warn("Encountered singularity in bootstrap iteration.\
                            Observation discarded.")
            pass
    # Compute and store Walpha_b
    Walpha_b = Gamma[:, -1].T.dot(Gamma[:, -1])

    return Walpha_b

def _BS_Walpha_sub_block(model, n, d, blocksize):

    model = deepcopy(model)

    X_b = np.full((model.L, model.T), np.nan)
    np.random.seed(n)

    n_pf = np.shape(d)[0]

    # Blockwise Residual Draw
    block_len = blocksize

    n_blocks = np.ceil(np.size(d, axis=1)/block_len)
    last_block = np.size(d, axis=1)%block_len
    d_temp = d.copy()

    # Loop over blocks
    for b in range(int(n_blocks)):
        # Loop over entities
        dof = 5
        tvar = dof / (dof-2)
        block_rv = (1/np.sqrt(tvar))*np.random.standard_t(dof)
        
        block_rv = np.random.standard_t(dof)

        if last_block == 0:
            rand_block = np.random.randint(0,high=n_blocks)
        else:
            rand_block = np.random.randint(0,high=n_blocks-1)

        if b < n_blocks-1:
            d_temp[:, b*block_len:(b+1)*block_len] = \
            d[:, block_len*rand_block:block_len*(rand_block+1)]*block_rv
            # d_temp[:, b*block_len:(b+1)*block_len] = \
            # d[np.random.randint(0,high=n_pf-1,size=(n_pf,)), block_len*rand_block:block_len*(rand_block+1)]*block_rv
        elif last_block > 0:
            d_temp[:, b*block_len:b*block_len+last_block] = \
            d[:, block_len*rand_block:block_len*rand_block+last_block]*block_rv
            # d_temp[:, b*block_len:b*block_len+last_block] = \
            # d[np.random.randint(0,high=n_pf-1,size=(n_pf,)), block_len*rand_block:block_len*rand_block+last_block]*block_rv
    for t in range(model.T):
        X_b[:, t] = model.W[:, :, t].dot(model.Gamma_Est[:, :-1])\
            .dot(model.Factors_Est[:-1, t]) + d_temp[:, t]

    Gamma = None
    while Gamma is None:
        try:
            # Re-estimate unrestricted model
            Gamma, Factors = model._fit_ipca(X=X_b, W=model.W, val_obs=model.val_obs,
                                             PSF=model.PSF, quiet=True)
        except np.linalg.LinAlgError:
            warnings.warn("Encountered singularity in bootstrap iteration.\
                           Observation discarded.")
            pass

    # Compute and store Walpha_b
    Walpha_b = Gamma[:, -1].T.dot(Gamma[:, -1])

    return  Walpha_b

def _BS_Walpha_sub_block_group(model, n, d, blocksize, alpha_index):

    model = deepcopy(model)

    X_b = np.full((model.L, model.T), np.nan)
    np.random.seed(n)

    n_pf = np.shape(d)[0]

    # Blockwise Residual Draw
    block_len = blocksize

    n_blocks = np.ceil(np.size(d, axis=1)/block_len)
    last_block = np.size(d, axis=1)%block_len
    d_temp = d.copy()

    # Loop over blocks
    for b in range(int(n_blocks)):
        # Loop over entities
        dof = 5
        tvar = dof / (dof-2)
        block_rv = (1/np.sqrt(tvar))*np.random.standard_t(dof)
        
        block_rv = np.random.standard_t(dof)

        if last_block == 0:
            rand_block = np.random.randint(0,high=n_blocks)
        else:
            rand_block = np.random.randint(0,high=n_blocks-1)

        if b < n_blocks-1:
            d_temp[:, b*block_len:(b+1)*block_len] = \
            d[:, block_len*rand_block:block_len*(rand_block+1)]*block_rv
            # d_temp[:, b*block_len:(b+1)*block_len] = \
            # d[np.random.randint(0,high=n_pf-1,size=(n_pf,)), block_len*rand_block:block_len*(rand_block+1)]*block_rv
        elif last_block > 0:
            d_temp[:, b*block_len:b*block_len+last_block] = \
            d[:, block_len*rand_block:block_len*rand_block+last_block]*block_rv
            # d_temp[:, b*block_len:b*block_len+last_block] = \
            # d[np.random.randint(0,high=n_pf-1,size=(n_pf,)), block_len*rand_block:block_len*rand_block+last_block]*block_rv
    for t in range(model.T):
#         X_b[:, t] = model.W[:, :, t].dot(model.Gamma_Est[:, :-1])\
#             .dot(model.Factors_Est[:-1, t]) + d_temp[:, t]
        X_b[:, t] = model.W[:, :, t].dot(model.Gamma_Est).\
                dot(model.Factors_Est[:, t]) - \
                    model.W[:, alpha_index, t].dot(model.Gamma_Est[alpha_index, -1]).\
                dot(model.Factors_Est[-1, t]) + d_temp[:, t]

    Gamma = None
    while Gamma is None:
        try:
            # Re-estimate unrestricted model
            Gamma, Factors = model._fit_ipca(X=X_b, W=model.W, val_obs=model.val_obs,
                                             PSF=model.PSF, quiet=True)
        except np.linalg.LinAlgError:
            warnings.warn("Encountered singularity in bootstrap iteration.\
                           Observation discarded.")
            pass

    # Compute and store Walpha_b
    Walpha_b = Gamma[alpha_index, -1].T.dot(Gamma[alpha_index, -1])

    return  Walpha_b



def _BS_Wbeta_sub_block(model, n, d, l, g, blocksize):
    X_b = np.full((model.L, model.T), np.nan)
    np.random.seed(n)
    #Modify Gamma_beta such that its l-th row is zero at factor is zero
    Gamma_beta_l = np.copy(model.Gamma_Est)
    Gamma_beta_l[l, g] = 0
    Gamma = None
    n_pf = np.shape(d)[0]


    # Blockwise Residual Draw
    block_len = blocksize

    n_blocks = np.ceil(np.size(d, axis=1)/block_len)
    last_block = np.size(d, axis=1)%block_len
    d_temp = d.copy()

    # Loop over blocks
    for b in range(int(n_blocks)):
        # Loop over entities
        dof = 5
        tvar = dof / (dof-2)
        block_rv = (1/np.sqrt(tvar))*np.random.standard_t(dof)

        if last_block == 0:
            rand_block = np.random.randint(0,high=n_blocks)
        else:
            rand_block = np.random.randint(0,high=n_blocks-1)

        if b < n_blocks-1:
            d_temp[:, b*block_len:(b+1)*block_len] = \
            d[:, block_len*rand_block:block_len*(rand_block+1)]*block_rv
            # d_temp[:, b*block_len:(b+1)*block_len] = \
            # d[np.random.randint(0,high=n_pf-1,size=(n_pf,)), block_len*rand_block:block_len*(rand_block+1)]*block_rv
        elif last_block > 0:
            d_temp[:, b*block_len:b*block_len+last_block] = \
            d[:, block_len*rand_block:block_len*rand_block+last_block]*block_rv
            # d_temp[:, b*block_len:b*block_len+last_block] = \
            # d[np.random.randint(0,high=n_pf-1,size=(n_pf,)), block_len*rand_block:block_len*rand_block+last_block]*block_rv
    while Gamma is None:
        try:
            for t in range(model.T):
                X_b[:, t] = model.W[:, :, t].dot(Gamma_beta_l)\
                    .dot(model.Factors_Est[:, t]) + d_temp[:, t]

            Gamma, Factors = model._fit_ipca(X=X_b, W=model.W, val_obs=model.val_obs,
                                             PSF=model.PSF, quiet=True)

        except np.linalg.LinAlgError:
            warnings.warn("Encountered singularity in bootstrap iteration.\
                           Observation discarded.")
            pass

    # Compute and store Walpha_b
    Wbeta_l_b = np.squeeze(Gamma[l, g].reshape((1, -1)).dot(Gamma[l, g].reshape((1, -1)).T))
    return float(Wbeta_l_b)


def _BS_Wdelta_sub_block(model, n, d, l_delta, blocksize):
    X_b = np.full((model.L, model.T), np.nan)
    np.random.seed(n)

    L, Ktilde = np.shape(model.Gamma_Est)
    K_PSF, _ = np.shape(model.PSF)
    K = Ktilde - K_PSF - l_delta + 1
    n_pf = np.shape(d)[0]

    # Blockwise Residual Draw
    block_len = blocksize

    n_blocks = np.ceil(np.size(d, axis=1)/block_len)
    last_block = np.size(d, axis=1)%block_len
    d_temp = d.copy()

    # Loop over blocks
    for b in range(int(n_blocks)):
        # Loop over entities
        dof = 5
        tvar = dof / (dof-2)
        block_rv = (1/np.sqrt(tvar))*np.random.standard_t(dof)



        if last_block == 0:
            rand_block = np.random.randint(0,high=n_blocks)
        else:
            rand_block = np.random.randint(0,high=n_blocks-1)

        if b < n_blocks-1:
            d_temp[:, b*block_len:(b+1)*block_len] = \
            d[:, block_len*rand_block:block_len*(rand_block+1)]*block_rv
            # d_temp[:, b*block_len:(b+1)*block_len] = \
            # d[np.random.randint(0,high=n_pf-1,size=(n_pf,)), block_len*rand_block:block_len*(rand_block+1)]*block_rv
        elif last_block > 0:
            d_temp[:, b*block_len:b*block_len+last_block] = \
            d[:, block_len*rand_block:block_len*rand_block+last_block]*block_rv
            # d_temp[:, b*block_len:b*block_len+last_block] = \
            # d[np.random.randint(0,high=n_pf-1,size=(n_pf,)), block_len*rand_block:block_len*rand_block+last_block]*block_rv

    Gamma_Est_CF = np.copy(model.Gamma_Est)
    # Counterfactual Gamma with zeroed coeff on PSF
    Gamma_Est_CF[:, -l_delta] = 0
    for t in range(model.T):
        X_b[:, t] = model.W[:, :, t].dot(Gamma_Est_CF)\
            .dot(model.Factors_Est[:, t]) + d_temp[:, t]

    Gamma = None
    while Gamma is None:
        try:
            # Re-estimate unrestricted model
            Gamma, Factors = model._fit_ipca(X=X_b, W=model.W, val_obs=model.val_obs,
                                             PSF=model.PSF, quiet=False)
        except np.linalg.LinAlgError:
            warnings.warn("Encountered singularity in bootstrap iteration.\
                           Observation discarded.")
            pass



    # Compute and store Walpha_b
    Wdelta_b = (Gamma[:, -l_delta].reshape((-1, 1), order="F")).T.dot(Gamma[:, -l_delta].reshape((-1, 1), order="F"))

    return np.squeeze(Wdelta_b)


@jit(nopython=True)
def _numba_solve(m1, m2):
    return np.linalg.solve(np.ascontiguousarray(m1), np.ascontiguousarray(m2))

@jit(nopython=True)
def _numba_lstsq(m1, m2):
    return np.linalg.lstsq(np.ascontiguousarray(m1), np.ascontiguousarray(m2))

@jit(nopython=True)
def _numba_kron(m1, m2):
    return np.kron(np.ascontiguousarray(m1), np.ascontiguousarray(m2))

@jit(nopython=True)
def _numba_chol(m1):
    return np.linalg.cholesky(np.ascontiguousarray(m1))

@jit(nopython=True)
def _numba_svd(m1):
    return np.linalg.svd(np.ascontiguousarray(m1))

@jit(nopython=True)
def _numba_full(m1, m2):
    return np.full(m1, m2)
```


## `replication/Data/data_codes/data_chrs.py`

Computes the 35 asset characteristics in Table 1 (and Appendix B). Use this to answer questions like "how exactly is `max30` / `illiq` / `co-skew` computed?" with the actual formula instead of a paraphrase.

```python
import numpy as np
import pandas as pd
import statsmodels.api as sm
from tqdm import tqdm

def amihud_illiquidity(df):
    """
    Calculate Amihud (2002) illiquidity measure.
    
    Parameters:
    df (DataFrame): DataFrame with 'logret' and 'volumeto' columns
    
    Returns:
    Series: Amihud illiquidity measure
    """
    # Create a copy to avoid warnings about modifying the original dataframe
    
    # Replace zero volumes with NaN to avoid division by zero
    df['volumeto'] = df['volumeto'].replace(0, np.nan)
    
    # Calculate Amihud measure: |return| / volume
    df['amihud'] = 100000 * np.abs(df['logret'])/df['volumeto']
    
    # Use 30-day rolling mean of the Amihud ratio
    amihud = df['amihud'].rolling(window=30).mean()
    
    # Replace infinite and NaN values
    amihud = amihud.replace([np.inf, -np.inf], np.nan)
    
    return amihud


def corwin_schultz(df):
    D = pd.DataFrame()
    k = 3 - (2 * np.sqrt(2))
    
    # Extract price data
    D['H'] = df.high
    D['L'] = df.low
    
    # Replace zeros with small positive values to avoid log(0) errors
    D['H'] = D['H'].replace(0, np.nan)
    D['L'] = D['L'].replace(0, np.nan)
    
    # Get lagged values
    D['H_lagged'] = df.high.shift(1)
    D['L_lagged'] = df.low.shift(1)
    
    # Also replace zeros in lagged values
    D['H_lagged'] = D['H_lagged'].replace(0, np.nan)
    D['L_lagged'] = D['L_lagged'].replace(0, np.nan)
    
    # Calculate beta with error handling
    D['beta'] = np.log(D.H/D.L)**2 + np.log(D.H_lagged/D.L_lagged)**2
    
    D['minL'] = D[['L','L_lagged']].min(axis=1)
    D['maxH'] = D[['H','H_lagged']].max(axis=1)
    
    # Handle potential zero values in minL
    D['minL'] = D['minL'].replace(0, np.nan)
    
    D['gamma'] = np.log((D['maxH']/D['minL']))**2
    
    D['alpha'] = ((np.sqrt(2*D.beta) - np.sqrt(D.beta)) / k) - np.sqrt(D.gamma/k)
    
    D['S'] = (2 * (np.exp(D.alpha)-1)) / (1 + np.exp(D.alpha))
    D.loc[D.S < 0, 'S'] = 0
    D.loc[np.isnan(D.S), 'S'] = 0
    
    D['sroll'] = D.S.rolling(7).mean()
    D.loc[D.S == 0, 'S'] = D.sroll
    
    return D['S']


def abdi_ranaldo(df):
    D = pd.DataFrame()
    
    # Extract price data
    D['H'] = df.high
    D['L'] = df.low
    D['C'] = df.close
    
    # Replace zeros with NaN to avoid log(0) errors
    D['H'] = D['H'].replace(0, np.nan)
    D['L'] = D['L'].replace(0, np.nan)
    D['C'] = D['C'].replace(0, np.nan)
    
    # Get lagged values
    D['H_lagged'] = df.high.shift(1)
    D['L_lagged'] = df.low.shift(1)
    
    # Also replace zeros in lagged values
    D['H_lagged'] = D['H_lagged'].replace(0, np.nan)
    D['L_lagged'] = D['L_lagged'].replace(0, np.nan)
    
    # Calculate midpoint prices safely
    D['n_lagged'] = (np.log(D['H_lagged']) + np.log(D['L_lagged'])) / 2
    D['n_forward'] = (np.log(D['H']) + np.log(D['L'])) / 2
    
    # Calculate spread measure with NaN propagation
    D['S'] = 4 * (np.log(D['C']) - D['n_lagged']) * (np.log(D['C']) - D['n_forward'])
    
    # Replace negative values with zero BEFORE taking square root
    D.loc[D['S'] < 0, 'S'] = 0
    D.loc[np.isnan(D.S), 'S'] = 0
    
    # Apply rolling mean to replace zeros if needed
    D['sroll'] = D['S'].rolling(7).mean()
    D.loc[D['S'] == 0, 'S'] = D['sroll']
    
    # NOW take square root after ensuring all values are non-negative
    D['S'] = np.sqrt(D['S'])
    
    return D['S']


def calculate_volume_shocks(df, volume_col='volumeto', window_lengths=30):
    """Calculate volume shocks.

    Paper definition
    ----------------
    Log daily trading volume minus its trend in the previous L days.

    Implementation
    --------------
    For each ticker:
      vol_shock_L = log(1+volume) - rolling_mean_L(log(1+volume))

    Notes
    -----
    - Expects a MultiIndex with level 'ticker'.
    - This function is vectorized (groupby+rolling) to avoid per-row loops.
    """
    result_df = df.copy()

    if not isinstance(result_df.index, pd.MultiIndex) or 'ticker' not in result_df.index.names:
        raise ValueError("calculate_volume_shocks expects a MultiIndex with level 'ticker'")

    if isinstance(window_lengths, int):
        window_lengths = [window_lengths]

    # Work on log(1+vol) to handle zeros
    v = result_df[volume_col].astype(float)
    vlog = np.log(v + 1.0)

    g = vlog.groupby(level='ticker')

    for l in window_lengths:
        roll_mean = g.rolling(window=l, min_periods=l).mean().reset_index(level=0, drop=True)
        # Keep existing naming convention used downstream
        result_df[f'volshockSTD{l}'] = vlog - roll_mean

    return result_df


def calculate_value_weighted_index(df, return_col='logret', market_cap_col='marketcap'):
    """
    Calculate the return on a value-weighted market portfolio.
    
    Parameters:
    -----------
    df : pandas.DataFrame
        DataFrame with returns and market cap data, indexed by [date, ticker]
    return_col : str, default 'logret'
        Name of the column containing returns
    market_cap_col : str, default 'marketcap'
        Name of the column containing market capitalization
        
    Returns:
    --------
    pandas.DataFrame
        Original DataFrame with an added value-weighted index column
    """
    # Make a copy to avoid modifying the original
    result_df = df.copy()
    
    # Extract the 'date' level for grouping
    dates = result_df.index.get_level_values('date')
    
    # Calculate value weights for each asset on each date
    weights = result_df.groupby(dates)[market_cap_col].transform(
        lambda x: x / np.nansum(x)
    )
    result_df['value-weights-idx'] = weights
    
    # Replace invalid values with 0
    result_df['value-weights-idx'] = result_df['value-weights-idx'].replace(
        [np.nan, np.inf, -np.inf], 0
    )
    
    # Calculate the value-weighted index return for each date
    idx_vw = result_df.groupby(dates)[[return_col, 'value-weights-idx']].apply(
        lambda x: np.nansum(x[return_col] * x['value-weights-idx'])
    ).to_frame()
    
    # Name the column and handle invalid values
    idx_vw.columns = ['vw-index']
    idx_vw = idx_vw.replace([0, np.inf, -np.inf], np.nan)
    
    # Set the index name to 'date' for proper merging
    idx_vw.index.name = 'date'
    
    # Merge the index back into the main DataFrame
    # First get the unique index levels
    idx_names = result_df.index.names
    
    # Reset index to prepare for merge
    result_df = result_df.reset_index()
    
    # Merge the value-weighted index
    result_df = result_df.merge(idx_vw, how='left', left_on='date', right_index=True)
    
    # Restore the original index structure
    result_df = result_df.set_index(idx_names)
    
    return result_df


def calculate_market_betas(df, return_col='logret', market_col='vw-index', window=30, min_periods=30):
    """
    Calculate market betas using rolling window regressions.

    Parameters:
    -----------
    df : pandas.DataFrame
        DataFrame with return data and market index, indexed by [date, ticker]
    return_col : str, default 'logret'
        Name of the column containing asset returns
    market_col : str, default 'vw-index'
        Name of the column containing market returns
    window : int, default 30
        Rolling window size for regression
    min_periods : int, default 30
        Minimum number of observations required for regression

    Returns:
    --------
    pandas.DataFrame
        Original DataFrame with added CAPM parameters (alpha, beta, idiosyncratic volatility)
    """
    # Function to run OLS regression and return parameters
    def beta_sub(ret, factors):
        """Run OLS(ret ~ 1 + factors) defensively.

        Returns [alpha, beta, idio_vol] or [nan, nan, nan] when the window is not usable.
        """
        try:
            ret = np.asarray(ret, dtype=float).reshape(-1)
            factors = np.asarray(factors, dtype=float)
            if factors.ndim == 1:
                factors = factors.reshape(-1, 1)

            # Basic shape / emptiness checks
            if ret.size == 0 or factors.size == 0:
                return [np.nan, np.nan, np.nan]
            if ret.shape[0] != factors.shape[0]:
                n = min(ret.shape[0], factors.shape[0])
                ret = ret[:n]
                factors = factors[:n, :]

            # Drop rows with any NaN/inf
            mask = np.isfinite(ret)
            mask &= np.all(np.isfinite(factors), axis=1)
            if mask.sum() < min_periods:
                return [np.nan, np.nan, np.nan]

            ret2 = ret[mask]
            fac2 = factors[mask]

            # Need variation in market factor; otherwise beta is undefined
            if fac2.shape[1] >= 1 and np.nanstd(fac2[:, 0]) == 0:
                return [np.nan, np.nan, np.nan]

            model = sm.OLS(ret2, sm.add_constant(fac2), missing='drop').fit()

            if len(model.params) >= 2 and np.isfinite(model.scale):
                return [model.params[0], model.params[1], float(np.sqrt(model.scale))]
            return [np.nan, np.nan, np.nan]

        except Exception as e:
            print(f"Regression error: {e}")
            return [np.nan, np.nan, np.nan]

    # Function to calculate rolling betas for a single ticker
    def beta_roll(dfstock, window, min_periods):
        beta = pd.DataFrame(index=range(0, len(dfstock)), columns=['A'])
        exret = dfstock[return_col].to_numpy(dtype=float)
        factors = dfstock[[market_col]].to_numpy(dtype=float)

        for i in range(len(dfstock)):
            if i + 1 < window:
                continue

            w_ret = exret[i + 1 - window : i + 1]
            w_fac = factors[i + 1 - window : i + 1, :]

            # Count usable observations (both ret and factor finite)
            mask = np.isfinite(w_ret) & np.isfinite(w_fac[:, 0])
            if mask.sum() < min_periods:
                continue

            beta.at[i, 'A'] = beta_sub(w_ret, w_fac)

        return beta['A'].tolist()
    
    # Make a copy and preserve original index structure
    result_df = df.copy()
    original_index = result_df.index.copy()
    
    # Reset index to work with plain columns
    if isinstance(result_df.index, pd.MultiIndex):
        result_df = result_df.reset_index()
    
    # Get unique tickers
    tickers = result_df['ticker'].unique()
    
    # Initialize list to store results
    all_results = []
    
    # Process each ticker with progress bar
    for ticker in tqdm(tickers, desc="Calculating market betas"):
        # Get data for this ticker
        ticker_df = result_df[result_df['ticker'] == ticker].copy()
        ticker_df = ticker_df.sort_values('date')
        
        # Calculate beta values
        beta_values = beta_roll(ticker_df, window, min_periods)
        
        # Create dataframes for ticker results with NaN for missing values
        dates = ticker_df['date'].values
        alphas = []
        betas = []
        idio_vols = []
        
        # Process each result individually
        for res in beta_values:
            if isinstance(res, list) and len(res) == 3:
                alphas.append(res[0])
                betas.append(res[1])
                idio_vols.append(res[2])
            else:
                alphas.append(np.nan)
                betas.append(np.nan)
                idio_vols.append(np.nan)
        
        # Create a result dataframe
        ticker_result = pd.DataFrame({
            'date': dates,
            'ticker': ticker,
            'capm_alpha': alphas,
            'capm_beta': betas,
            'idio_vol': idio_vols
        })
        
        all_results.append(ticker_result)
    
    # Combine all results
    combined_results = pd.concat(all_results, ignore_index=True)
    
    # Merge back with the original dataframe
    result_df = result_df.merge(
        combined_results[['date', 'ticker', 'capm_alpha', 'capm_beta', 'idio_vol']], 
        on=['date', 'ticker'], 
        how='left'
    )
    
    # Restore the original index structure
    result_df = result_df.set_index(original_index.names)
    
    return result_df


def calculate_momentum(df, return_col='logret', lookback_periods=None, custom_periods=None):
    """
    Calculate momentum returns for various lookback periods.
    
    Parameters:
    -----------
    df : pandas.DataFrame
        DataFrame with return data indexed by [date, ticker]
    return_col : str, default 'logret'
        Name of the column containing returns
    lookback_periods : list, default [7, 13, 22, 31]
        List of lookback periods for standard momentum calculation (l-1 day)
    custom_periods : list of tuples, default [(31, 13), (180, 60)]
        List of (longer_period, shorter_period) tuples for custom lookback calculations
        
    Returns:
    --------
    pandas.DataFrame
        Original DataFrame with added momentum columns
    """
    # Set default values if not provided
    if lookback_periods is None:
        lookback_periods = [7, 13, 22, 31]
    
    if custom_periods is None:
        custom_periods = [(31, 13), (180, 60)]
    
    # Make a copy to avoid modifying the original
    result_df = df.copy()
    
    # Store original index for later reconstruction
    original_index = result_df.index.copy()
    
    # Reset index to avoid MultiIndex issues
    result_df = result_df.reset_index()
    
    # Get list of unique tickers
    tickers = result_df['ticker'].unique()
    
    # Initialize an empty DataFrame to store all results
    momentum_results = pd.DataFrame()
    
    # Process each ticker separately
    for ticker in tickers:
        # Get data for this ticker and sort by date
        ticker_data = result_df[result_df['ticker'] == ticker].copy().sort_values('date')
        
        # Calculate standard momentum
        for l in lookback_periods:
            ticker_data[f'r{l}_1'] = (
                ticker_data[return_col].rolling(l).sum() - 
                ticker_data[return_col].rolling(1).sum()
            )
        
        # Calculate custom momentum
        for longer, shorter in custom_periods:
            ticker_data[f'r{longer}_{shorter}'] = (
                ticker_data[return_col].rolling(longer).sum() - 
                ticker_data[return_col].rolling(shorter).sum()
            )
        
        # Append to results
        momentum_results = pd.concat([momentum_results, ticker_data], ignore_index=True)
    
    # Merge the momentum metrics back to the original DataFrame
    momentum_columns = ([f'r{l}_1' for l in lookback_periods] + 
                         [f'r{l}_{s}' for l, s in custom_periods])
    
    # Merge with original data
    result_df = result_df.merge(
        momentum_results[['date', 'ticker'] + momentum_columns],
        on=['date', 'ticker'],
        how='left'
    )
    
    # Restore original index structure
    result_df = result_df.set_index(original_index.names)
    
    return result_df


def calculate_max_return(df, return_col='logret', window=30, top_n_avg=None):
    """
    Calculate the maximum return and optionally the average of top N returns over a rolling window.
    
    Parameters:
    -----------
    df : pandas.DataFrame
        DataFrame with return data indexed by [date, ticker]
    return_col : str, default 'logret'
        Name of the column containing return data
    window : int, default 30
        Rolling window size for max calculation
    top_n_avg : int, optional
        If provided, calculate the average of the top N highest returns in the window
        
    Returns:
    --------
    pandas.DataFrame
        Original DataFrame with added 'max' column and optionally 'topN_avg' column
    """
    # Make a copy to avoid modifying the original
    result_df = df.copy()
    
    # Store original index for later reconstruction
    original_index = result_df.index.copy()
    
    # Reset index to avoid MultiIndex issues
    result_df = result_df.reset_index()
    
    # Get list of unique tickers
    tickers = result_df['ticker'].unique()
    
    # Initialize DataFrame to store results
    all_results = pd.DataFrame()
    
    # Process each ticker separately
    for ticker in tqdm(tickers, desc="Calculating max return"):
        # Get data for this ticker and sort by date
        ticker_data = result_df[result_df['ticker'] == ticker].copy().sort_values('date')
        
        # Calculate max return over window
        ticker_data[f'max{window}'] = ticker_data[return_col].rolling(window, center=False).max()
        
        # If top_n_avg is specified, calculate average of top N returns
        if top_n_avg is not None:
            # Function to calculate average of top N returns
            def avg_top_n(series, n):
                if len(series) == 0 or series.isna().all():
                    return np.nan
                # Sort the non-NaN values in descending order and take top N
                sorted_vals = series.dropna().sort_values(ascending=False)
                if len(sorted_vals) < n:
                    return np.nan
                # Return the average of top N values
                return sorted_vals.iloc[:n].mean()
            
            # Apply the function using rolling window
            top_n_avgs = []
            for i in range(len(ticker_data)):
                if i+1 < window:
                    top_n_avgs.append(np.nan)
                else:
                    window_data = ticker_data[return_col].iloc[i+1-window:i+1]
                    top_n_avgs.append(avg_top_n(window_data, top_n_avg))
            
            # Add to ticker data
            ticker_data[f'max{window}_{top_n_avg}'] = top_n_avgs
            
            # Prepare columns for results
            result_cols = ['date', 'ticker', f'max{window}', f'max{window}_{top_n_avg}']
        else:
            result_cols = ['date', 'ticker', f'max{window}']
        
        # Append to results
        all_results = pd.concat([all_results, ticker_data[result_cols]], ignore_index=True)
    
    # Merge the metrics back to the original DataFrame
    result_df = result_df.merge(
        all_results,
        on=['date', 'ticker'],
        how='left'
    )
    
    # Restore original index structure
    result_df = result_df.set_index(original_index.names)
    
    return result_df


def calculate_relative_to_high(df, price_col='close', window=30):
    """
    Calculate the relative-to-high price ratio over a rolling window.
    
    Parameters:
    -----------
    df : pandas.DataFrame
        DataFrame with price data indexed by [date, ticker]
    price_col : str, default 'close'
        Name of the column containing price data
    window : int, default 30
        Rolling window size for max calculation
        
    Returns:
    --------
    pandas.DataFrame
        Original DataFrame with added 'rel_to_high' column
    """
    # Make a copy to avoid modifying the original
    result_df = df.copy()
    
    # Store original index for later reconstruction
    original_index = result_df.index.copy()
    
    # Reset index to avoid MultiIndex issues
    result_df = result_df.reset_index()
    
    # Get list of unique tickers
    tickers = result_df['ticker'].unique()
    
    # Initialize DataFrame to store results
    all_results = pd.DataFrame()
    
    # Process each ticker separately
    for ticker in tqdm(tickers, desc="Calculating relative-to-high"):
        # Get data for this ticker and sort by date
        ticker_data = result_df[result_df['ticker'] == ticker].copy().sort_values('date')
        
        # Calculate max price over window
        max_price = ticker_data[price_col].rolling(window, center=False).max()
        
        # Calculate relative-to-high (using price from previous day divided by max price)
        ticker_data['rel_to_high'] = ticker_data[price_col].shift(1) / max_price
        
        # Append to results
        all_results = pd.concat([all_results, ticker_data[['date', 'ticker', 'rel_to_high']]], ignore_index=True)
    
    # Merge the rel_to_high metric back to the original DataFrame
    result_df = result_df.merge(
        all_results[['date', 'ticker', 'rel_to_high']],
        on=['date', 'ticker'],
        how='left'
    )
    
    # Restore original index structure
    result_df = result_df.set_index(original_index.names)
    
    return result_df


def calculate_crypto_book_to_market(df, addresses_col='unique_addresses_all_time', market_cap_col='marketcap'):
    """
    Calculate crypto book-to-market ratio using unique addresses as proxy for book value.
    
    Parameters:
    -----------
    df : pandas.DataFrame
        DataFrame with addresses and market cap data
    addresses_col : str, default 'unique_addresses_all_time'
        Name of the column containing unique addresses data
    market_cap_col : str, default 'marketcap'
        Name of the column containing market capitalization data
        
    Returns:
    --------
    pandas.DataFrame
        Original DataFrame with added 'bm' column
    """
    # Make a copy to avoid modifying the original
    result_df = df.copy()
    
    # Calculate book-to-market ratio
    result_df['bm'] = result_df[addresses_col] / result_df[market_cap_col]
    
    # Handle infinite values
    result_df = result_df.replace([np.inf, -np.inf], np.nan)
    
    return result_df


def calculate_detrended_turnover(df, volume_col='volumeto', market_cap_col='marketcap', 
                               turnover_col='turnover', window=180):
    """Calculate de-trended volume minus market turnover."""
    # Make a copy to avoid modifying the original
    result_df = df.copy()

    # Preserve original index order/names
    original_index_names = result_df.index.names if isinstance(result_df.index, pd.MultiIndex) else None

    # First, reset the index to work with regular columns
    temp_df = result_df.reset_index()

    # Group by date and calculate market turnover
    date_groups = temp_df.groupby('date')
    market_turnover = {}

    for date, group in date_groups:
        total_volume = group[volume_col].sum()
        total_mcap = group[market_cap_col].sum()
        market_to = total_volume / total_mcap if total_mcap > 0 else np.nan
        market_turnover[date] = market_to

    # Convert to Series
    market_to_series = pd.Series(market_turnover)

    # Cap extreme values at the median
    median_value = market_to_series.median()
    market_to_series[market_to_series > 1] = median_value

    # Handle invalid values
    market_to_series = market_to_series.replace([0, np.inf, -np.inf], np.nan)

    # Add market turnover to the temp dataframe
    temp_df['market-to'] = temp_df['date'].map(market_to_series)

    # Calculate turnover minus market turnover
    temp_df['dto'] = temp_df[turnover_col] - temp_df['market-to']

    # Detrend by subtracting the rolling median
    detrended_values = {}

    for ticker, group in temp_df.groupby('ticker'):
        sorted_group = group.sort_values('date')
        rolling_median = sorted_group['dto'].rolling(window=window, center=False).median()
        detrended = sorted_group['dto'] - rolling_median

        # Store results with index
        for idx, value in zip(sorted_group.index, detrended):
            detrended_values[idx] = value

    # Apply detrended values
    temp_df['dto'] = temp_df.index.map(detrended_values)

    # Restore the original index structure (keep ('ticker','date') order used by the pipeline)
    if original_index_names and set(original_index_names) >= {'ticker', 'date'}:
        temp_df = temp_df.set_index(list(original_index_names))
    else:
        temp_df = temp_df.set_index(['ticker', 'date'])

    return temp_df


def calculate_volatility_metrics(df, turnover_col='turnover', volume_col='volumeto', 
                               window=60, min_periods=30, log_transform_volume=True):
    """
    Calculate the volatility of turnover and volume.
    
    Parameters:
    -----------
    df : pandas.DataFrame
        DataFrame with turnover and volume data indexed by [date, ticker]
    turnover_col : str, default 'turnover'
        Name of the column containing turnover data
    volume_col : str, default 'volumeto'
        Name of the column containing volume data
    window : int, default 60
        Rolling window size for volatility calculation
    min_periods : int, default 30
        Minimum number of observations required in window
    log_transform_volume : bool, default True
        Whether to apply log transformation to volume before calculating volatility
        
    Returns:
    --------
    pandas.DataFrame
        Original DataFrame with added volatility columns ('std_to' and 'std_vol')
    """
    # Make a copy to avoid modifying the original
    result_df = df.copy()
    
    # Store original index structure
    original_index = result_df.index.copy()
    
    # Reset index to work with plain columns
    if isinstance(result_df.index, pd.MultiIndex):
        result_df = result_df.reset_index()
    
    # Get unique tickers
    tickers = result_df['ticker'].unique()
    
    # Initialize DataFrame to store results
    all_results = pd.DataFrame()
    
    # Process each ticker separately
    for ticker in tqdm(tickers, desc="Calculating volatility metrics"):
        # Get data for this ticker and sort by date
        ticker_data = result_df[result_df['ticker'] == ticker].copy().sort_values('date')
        
        # Function to calculate standardized volatility - fixed to handle numpy arrays properly
        def calc_volatility(series):
            if len(series) < min_periods:
                return np.nan
            # Check for NaN values
            valid_data = series[~np.isnan(series)]
            if len(valid_data) < min_periods:
                return np.nan
            # Demean and calculate standard deviation
            return np.nanstd(valid_data - np.nanmean(valid_data))
        
        # Calculate volatility of turnover
        ticker_data['std_to'] = ticker_data[turnover_col].rolling(
            window=window, 
            min_periods=min_periods
        ).apply(calc_volatility, raw=True)
        
        # Calculate volatility of volume
        if log_transform_volume:
            # Add 1 to volume to avoid log(0) issues and calculate log volume
            volume_data = np.log(ticker_data[volume_col] + 1)
        else:
            volume_data = ticker_data[volume_col]
            
        ticker_data['std_vol'] = volume_data.rolling(
            window=window, 
            min_periods=min_periods
        ).apply(calc_volatility, raw=True)
        
        # Append to results
        all_results = pd.concat([all_results, ticker_data], ignore_index=True)
    
    # Merge volatility metrics back to original data
    result_cols = list(set(result_df.columns) | {'std_to', 'std_vol'})
    result_df = all_results[result_cols]
    
    # Restore original index structure
    if isinstance(original_index, pd.MultiIndex):
        result_df = result_df.set_index(original_index.names)
    
    return result_df


def calculate_volume_cv(df, volume_col='volumeto', window=30, min_periods=15):
    """
    Calculate the coefficient of variation (std/mean) of trading volume over a rolling window.
    
    Parameters:
    -----------
    df : pandas.DataFrame
        DataFrame with volume data indexed by [date, ticker]
    volume_col : str, default 'volumeto'
        Name of the column containing volume data
    window : int, default 30
        Rolling window size for calculation
    min_periods : int, default 15
        Minimum number of observations required in window
        
    Returns:
    --------
    pandas.DataFrame
        Original DataFrame with added 'cv_vol' column
    """
    # Make a copy to avoid modifying the original
    result_df = df.copy()
    
    # Store original index structure
    original_index = result_df.index.copy()
    
    # Reset index to work with plain columns
    if isinstance(result_df.index, pd.MultiIndex):
        result_df = result_df.reset_index()
    
    # Get unique tickers
    tickers = result_df['ticker'].unique()
    
    # Initialize DataFrame to store results
    all_results = pd.DataFrame()
    
    # Process each ticker separately
    for ticker in tqdm(tickers, desc="Calculating volume CV"):
        # Get data for this ticker and sort by date
        ticker_data = result_df[result_df['ticker'] == ticker].copy().sort_values('date')
        
        # Calculate rolling mean
        rolling_mean = ticker_data[volume_col].rolling(window=window, min_periods=min_periods).mean()
        
        # Calculate rolling standard deviation
        rolling_std = ticker_data[volume_col].rolling(window=window, min_periods=min_periods).std()
        
        # Calculate coefficient of variation (std/mean)
        ticker_data['cv_vol'] = rolling_std / rolling_mean
        
        # Handle infinity and NaN values
        ticker_data['cv_vol'] = ticker_data['cv_vol'].replace([np.inf, -np.inf], np.nan)
        
        # Append to results
        all_results = pd.concat([all_results, ticker_data], ignore_index=True)
    
    # Select necessary columns
    result_cols = ['date', 'ticker', 'cv_vol']
    additional_cols = [col for col in all_results.columns if col not in result_cols]
    final_cols = result_cols + additional_cols
    
    # Merge volume CV back to original data
    result_df = all_results[final_cols]
    
    # Restore original index structure
    if isinstance(original_index, pd.MultiIndex):
        result_df = result_df.set_index(original_index.names)
    
    return result_df


def calculate_realized_skewness(df, return_col='logret', window=60, min_periods=30):
    """
    Calculate realized skewness using a rolling window of returns.
    
    Parameters:
    -----------
    df : pandas.DataFrame
        DataFrame with return data indexed by [date, ticker]
    return_col : str, default 'logret'
        Name of the column containing return data
    window : int, default 60
        Rolling window size for calculation
    min_periods : int, default 30
        Minimum number of observations required in window
        
    Returns:
    --------
    pandas.DataFrame
        Original DataFrame with added 'realized_skew' column
    """
    # Make a copy to avoid modifying the original
    result_df = df.copy()
    
    # Store original index structure
    original_index = result_df.index.copy()
    
    # Reset index to work with plain columns
    if isinstance(result_df.index, pd.MultiIndex):
        result_df = result_df.reset_index()
    
    # Get unique tickers
    tickers = result_df['ticker'].unique()
    
    # Initialize DataFrame to store results
    all_results = pd.DataFrame()
    
    # Function to calculate skewness
    def calc_skewness(series):
        # Remove NaN values
        series = series.dropna()
        
        # Check if we have enough data
        if len(series) < min_periods:
            return np.nan
        
        # Calculate mean and standard deviation
        mean = series.mean()
        std = series.std()
        
        # Avoid division by zero
        if std == 0:
            return np.nan
        
        # Calculate skewness
        n = len(series)
        skew = (np.sum((series - mean) ** 3) / n) / (std ** 3)
        
        return skew
    
    # Process each ticker separately
    for ticker in tqdm(tickers, desc="Calculating realized skewness"):
        # Get data for this ticker and sort by date
        ticker_data = result_df[result_df['ticker'] == ticker].copy().sort_values('date')
        
        # Calculate rolling skewness
        ticker_data[f'rskew_{window}'] = ticker_data[return_col].rolling(
            window=window, min_periods=min_periods
        ).apply(calc_skewness, raw=False)
        
        # Append to results
        all_results = pd.concat([all_results, ticker_data], ignore_index=True)
    
    # Select all columns
    result_cols = list(all_results.columns)
    
    # Merge skewness back to original data
    result_df = all_results[result_cols]
    
    # Restore original index structure
    if isinstance(original_index, pd.MultiIndex):
        result_df = result_df.set_index(original_index.names)
    
    return result_df


def calculate_coskewness(df, return_col='logret', market_return_col='vw-index', window=60, min_periods=30):
    """
    Calculate coskewness between individual assets and the market portfolio 
    following Harvey and Siddique (2000).
    
    Parameters:
    -----------
    df : pandas.DataFrame
        DataFrame with asset and market return data indexed by [date, ticker]
    return_col : str, default 'logret'
        Name of the column containing individual asset return data
    market_return_col : str, default 'vw-index'
        Name of the column containing market return data
    window : int, default 60
        Rolling window size for calculation
    min_periods : int, default 30
        Minimum number of observations required in window
        
    Returns:
    --------
    pandas.DataFrame
        Original DataFrame with added 'coskew' column
    """
    # Make a copy to avoid modifying the original
    result_df = df.copy()
    
    # Store original index structure
    original_index = result_df.index.copy()
    
    # Reset index to work with plain columns
    if isinstance(result_df.index, pd.MultiIndex):
        result_df = result_df.reset_index()
    
    # Get unique tickers
    tickers = result_df['ticker'].unique()
    
    # Initialize DataFrame to store results
    all_results = pd.DataFrame()
    
    # Function to calculate coskewness
    def calc_coskewness(group):
        # Extract returns and market returns
        returns = group[return_col].values
        market_returns = group[market_return_col].values
        
        # Remove rows with NaN values
        valid_idx = ~(np.isnan(returns) | np.isnan(market_returns))
        returns = returns[valid_idx]
        market_returns = market_returns[valid_idx]
        
        # Check if we have enough data
        if len(returns) < min_periods:
            return np.nan
        
        # Calculate means
        r_mean = np.mean(returns)
        rm_mean = np.mean(market_returns)
        
        # Calculate standard deviations
        r_std = np.std(returns)
        rm_std = np.std(market_returns)
        
        # Avoid division by zero
        if r_std == 0 or rm_std == 0:
            return np.nan
        
        # Calculate standardized returns
        r_std_series = (returns - r_mean) / r_std
        rm_std_series = (market_returns - rm_mean) / rm_std
        
        # Calculate coskewness as in Harvey and Siddique (2000)
        # E[(r_i - μ_i) * (r_m - μ_m)²] / (σ_i * σ_m²)
        coskew = np.mean(r_std_series * (rm_std_series ** 2))
        
        return coskew
    
    # Process each ticker separately
    for ticker in tqdm(tickers, desc="Calculating coskewness"):
        # Get data for this ticker and sort by date
        ticker_data = result_df[result_df['ticker'] == ticker].copy().sort_values('date')
        
        # Calculate rolling coskewness
        coskew_values = []
        for i in range(len(ticker_data)):
            if i+1 < window:
                coskew_values.append(np.nan)
            else:
                window_data = ticker_data.iloc[i+1-window:i+1]
                coskew_values.append(calc_coskewness(window_data))
        
        ticker_data['coskew'] = coskew_values
        
        # Append to results
        all_results = pd.concat([all_results, ticker_data], ignore_index=True)
    
    # Select all columns
    result_cols = list(all_results.columns)
    
    # Merge coskewness back to original data
    result_df = all_results[result_cols]
    
    # Restore original index structure
    if isinstance(original_index, pd.MultiIndex):
        result_df = result_df.set_index(original_index.names)
    
    return result_df


def calculate_ewma_volatility(df, return_col='logret', lambda_=0.96):
    """
    Calculate EWMA (Exponentially Weighted Moving Average) volatility for the entire time series.
    
    Parameters:
    -----------
    df : pandas.DataFrame
        DataFrame with return data indexed by [date, ticker]
    return_col : str, default 'logret'
        Name of the column containing return data
    lambda_ : float, default 0.96
        Decay factor - higher values give more weight to past observations
        
    Returns:
    --------
    pandas.DataFrame
        Original DataFrame with added 'ewma_vol' column
    """
    # Make a copy to avoid modifying the original
    result_df = df.copy()
    
    # Store original index structure
    original_index = result_df.index.copy()
    
    # Reset index to work with plain columns
    if isinstance(result_df.index, pd.MultiIndex):
        result_df = result_df.reset_index()
    
    # Get unique tickers
    tickers = result_df['ticker'].unique()
    
    # Initialize DataFrame to store results
    all_results = pd.DataFrame()
    
    # Process each ticker separately
    for ticker in tqdm(tickers, desc="Calculating EWMA volatility"):
        # Get data for this ticker and sort by date
        ticker_data = result_df[result_df['ticker'] == ticker].copy().sort_values('date')
        
        # Calculate squared returns
        ticker_data['sq_returns'] = ticker_data[return_col]**2
        
        # Calculate EWMA variance using the entire series
        ticker_data['ewma_var'] = ticker_data['sq_returns'].ewm(alpha=1-lambda_, adjust=False).mean()
        
        # Convert variance to volatility (standard deviation)
        ticker_data['ewma_vol'] = np.sqrt(ticker_data['ewma_var'])
        
        # Append to results
        all_results = pd.concat([all_results, ticker_data], ignore_index=True)
    
    # Select only necessary columns to return
    result_columns = list(result_df.columns) + ['ewma_vol']
    final_results = all_results[result_columns]
    
    # Restore original index structure
    if isinstance(original_index, pd.MultiIndex):
        idx_names = original_index.names
        final_results = final_results.set_index(idx_names)
    
    return final_results


def calculate_var(df, return_col='logret', window=90, confidence=0.05, min_periods=None):
    """
    Calculate historical Value at Risk (VaR) using rolling windows of returns.
    
    Parameters:
    -----------
    df : pandas.DataFrame
        DataFrame with return data indexed by [date, ticker]
    return_col : str, default 'logret'
        Name of the column containing return data
    window : int, default 90
        Rolling window size for VaR calculation
    confidence : float, default 0.05
        Confidence level for VaR (e.g., 0.05 for 95% VaR)
    min_periods : int, default None
        Minimum number of observations required in window. If None, defaults to window size.
        
    Returns:
    --------
    pandas.DataFrame
        Original DataFrame with added VaR column
    """
    # Set min_periods to window size if not specified
    if min_periods is None:
        min_periods = window
    
    # Make a copy to avoid modifying the original
    result_df = df.copy()
    
    # Store original index structure
    original_index = result_df.index.copy()
    
    # Reset index to work with plain columns
    if isinstance(result_df.index, pd.MultiIndex):
        result_df = result_df.reset_index()
    
    # Get unique tickers
    tickers = result_df['ticker'].unique()
    
    # Initialize DataFrame to store results
    all_results = pd.DataFrame()
    
    # Process each ticker separately
    for ticker in tqdm(tickers, desc=f"Calculating {int((1-confidence)*100)}% VaR"):
        # Get data for this ticker and sort by date
        ticker_data = result_df[result_df['ticker'] == ticker].copy().sort_values('date')
        
        # Function to calculate the VaR for each window
        def calc_var(window_returns):
            if len(window_returns) < min_periods:
                return np.nan
            # Sort returns and pick the value at the specified percentile
            percentile_idx = int(np.ceil(len(window_returns) * confidence)) - 1
            if percentile_idx < 0:  # Handle small window sizes
                percentile_idx = 0
            return sorted(window_returns)[percentile_idx]
        
        # Calculate VaR using rolling window
        var_values = []
        for i in range(len(ticker_data)):
            if i+1 < window:
                var_values.append(np.nan)
            else:
                window_returns = ticker_data[return_col].iloc[i+1-window:i+1].values
                var_values.append(calc_var(window_returns))
        
        ticker_data[f'var{int((1-confidence)*100)}'] = var_values
        
        # Append to results
        all_results = pd.concat([all_results, ticker_data], ignore_index=True)
    
    # Select all columns
    result_cols = list(all_results.columns)
    
    # Merge results back to original data
    result_df = all_results[result_cols]
    
    # Restore original index structure
    if isinstance(original_index, pd.MultiIndex):
        result_df = result_df.set_index(original_index.names)
    
    return result_df


def calculate_downside_beta(df, return_col='logret', market_col='vw-index', 
                           window=60, min_periods=30):
    """
    Calculate downside beta (beta conditional on negative market returns) for cryptocurrencies.
    
    Parameters:
    -----------
    df : pandas.DataFrame
        DataFrame with cryptocurrency and market return data
    return_col : str, default 'logret'
        Name of the column containing crypto returns
    market_col : str, default ''vw-index'
        Name of the column containing market returns
    window : int, default 60
        Rolling window size for beta calculation
    min_periods : int, default 30
        Minimum number of observations required in window
        
    Returns:
    --------
    pandas.DataFrame
        Original DataFrame with added 'downside_beta' column
    """
    # Make a copy to avoid modifying the original
    result_df = df.copy()
    
    # Store original index structure
    original_index = result_df.index.copy()
    
    # Reset index to work with plain columns
    if isinstance(result_df.index, pd.MultiIndex):
        result_df = result_df.reset_index()
    
    # Get unique tickers
    tickers = result_df['ticker'].unique()
    
    # Initialize DataFrame to store results
    all_results = pd.DataFrame()
    
    # Function to calculate downside beta   
    def calc_downside_beta(returns, market_returns):
        # Keep only observations with negative market returns
        mask = market_returns < 0
        down_returns = returns[mask]
        down_market = market_returns[mask]
        
        # Check if we have enough data
        if len(down_returns) < min_periods:
            return np.nan
        
        try:
            # Add constant for regression (intercept)
            X = sm.add_constant(down_market)
            # Run regression
            model = sm.OLS(down_returns, X, missing='drop').fit()
            # Extract beta (slope coefficient)
            beta = model.params[1]
            return beta
        except:
            return np.nan
    
    # Process each ticker separately
    for ticker in tqdm(tickers, desc="Calculating downside beta"):
        # Get data for this ticker and sort by date
        ticker_data = result_df[result_df['ticker'] == ticker].copy().sort_values('date')
        
        # Calculate rolling downside beta
        down_betas = []
        for i in range(len(ticker_data)):
            if i+1 < window:
                down_betas.append(np.nan)
            else:
                crypto_returns = ticker_data[return_col].iloc[i+1-window:i+1].values
                market_returns = ticker_data[market_col].iloc[i+1-window:i+1].values
                down_betas.append(calc_downside_beta(crypto_returns, market_returns))
        
        ticker_data['downside_beta'] = down_betas
        
        # Append to results
        all_results = pd.concat([all_results, ticker_data], ignore_index=True)
    
    # Select necessary columns
    result_cols = list(result_df.columns) + ['downside_beta']
    final_results = all_results[result_cols]
    
    # Restore original index structure
    if isinstance(original_index, pd.MultiIndex):
        final_results = final_results.set_index(original_index.names)
    
    return final_results







def check_missingness(df, by_ticker=False, verbose=True):
    """
    Check the level of missingness for all variables in a panel dataframe.
    
    Parameters:
    -----------
    df : pandas.DataFrame
        Panel dataframe with potentially missing values
    by_ticker : bool, default False
        Whether to report missingness by ticker as well as overall
    verbose : bool, default True
        Whether to print missingness statistics
        
    Returns:
    --------
    pandas.DataFrame
        Report of missingness percentage for each column
    """
    # Get total number of observations
    total_obs = len(df)
    
    if verbose:
        print(f"Total observations: {total_obs}")
    
    # Calculate missing value percentage for each column
    missing_stats = {}
    for col in df.columns:
        missing_count = df[col].isna().sum()
        missing_pct = (missing_count / total_obs) * 100
        missing_stats[col] = {'count': missing_count, 'percentage': missing_pct}
    
    # Create a missingness report dataframe
    missingness_report = pd.DataFrame({
        'missing_count': [stats['count'] for stats in missing_stats.values()],
        'missing_percentage': [stats['percentage'] for stats in missing_stats.values()]
    }, index=missing_stats.keys())
    
    # Sort by percentage of missing values (descending)
    missingness_report = missingness_report.sort_values('missing_percentage', ascending=False)
    
    if verbose:
        print("\nOverall Missingness Report:")
        print(missingness_report)
    
    # Check missingness by ticker if requested
    if by_ticker and 'ticker' in df.index.names:
        ticker_reports = {}
        
        # Get list of tickers
        tickers = df.index.get_level_values('ticker').unique()
        
        for ticker in tqdm(tickers, desc="Analyzing by ticker"):
            ticker_data = df.xs(ticker, level='ticker')
            ticker_obs = len(ticker_data)
            
            ticker_missing = {}
            for col in df.columns:
                missing_count = ticker_data[col].isna().sum()
                missing_pct = (missing_count / ticker_obs) * 100
                ticker_missing[col] = missing_pct
            
            ticker_reports[ticker] = ticker_missing
        
        # Create a dataframe with missingness by ticker
        ticker_missingness = pd.DataFrame(ticker_reports).T
        
        if verbose:
            print("\nMissingness Report by Ticker (Top 5 tickers):")
            print(ticker_missingness.head())
        
        return missingness_report, ticker_missingness
    
    return missingness_report

def check_average_missingness_by_crypto(df):
    """
    Check the level of missingness for all variables in a panel dataframe,
    averaged across cryptocurrencies.
    
    Parameters:
    -----------
    df : pandas.DataFrame
        Panel dataframe with multi-index including 'ticker'
        
    Returns:
    --------
    pandas.DataFrame
        Report of average missingness percentage for each column across cryptos
    """
    # Make sure the index is properly set up
    if 'ticker' not in df.index.names:
        raise ValueError("DataFrame index must contain 'ticker' level")
    
    # Get list of tickers
    tickers = df.index.get_level_values('ticker').unique()
    num_tickers = len(tickers)
    
    print(f"Analyzing missingness across {num_tickers} cryptocurrencies")
    
    # Initialize dictionary to store results
    missingness_by_var = {col: [] for col in df.columns}
    
    # Calculate missingness for each ticker
    for ticker in tqdm(tickers, desc="Processing cryptocurrencies"):
        # Get data for this ticker
        ticker_data = df.xs(ticker, level='ticker')
        ticker_obs = len(ticker_data)
        
        # Calculate missing percentage for each column
        for col in df.columns:
            missing_count = ticker_data[col].isna().sum()
            missing_pct = (missing_count / ticker_obs) * 100
            missingness_by_var[col].append(missing_pct)
    
    # Calculate average missingness across cryptocurrencies
    avg_missingness = {}
    for col, values in missingness_by_var.items():
        avg_missingness[col] = sum(values) / num_tickers
    
    # Create and sort the report dataframe
    missingness_report = pd.DataFrame({
        'avg_missing_percentage': avg_missingness
    }).sort_values('avg_missing_percentage', ascending=False)
    
    missingness_report.to_csv('missingness_report.csv', index=True)
    
    return missingness_report


''' Merge the crypto data with the stock market returns '''

def prepare_and_merge_ff_factors(crypto_df, ff_csv_path):
    """
    Prepare Fama-French factors from CSV and merge with cryptocurrency data.
    
    Parameters:
    -----------
    crypto_df : pandas.DataFrame
        Panel dataframe of cryptocurrencies with date in index or as a column
    ff_csv_path : str
        Path to the Fama-French factors CSV file
        
    Returns:
    --------
    pandas.DataFrame
        Merged dataframe with forward-filled factors
    """
    # Read the Fama-French factors CSV
    ff_factors = pd.read_csv(ff_csv_path)
    
    # Convert the date format (assuming it's in YYYYMMDD format)
    ff_factors['date'] = pd.to_datetime(ff_factors['date'], format='%Y%m%d')
    
    # Set date as index
    ff_factors = ff_factors.set_index('date')
        
    # Rename columns for clarity
    ff_factors = ff_factors.rename(columns={
        'Mkt-RF': 'market_excess_return',
        'SMB': 'size_factor',
        'HML': 'value_factor',
        'RMW': 'profitability_factor',
        'CMA': 'investment_factor',
        'RF': 'risk_free_rate'
    })
    
    # Calculate total market return
    ff_factors['market_return'] = ff_factors['market_excess_return'] + ff_factors['risk_free_rate']
    
    # Make a copy of crypto dataframe
    result_df = crypto_df.copy()
    
    # Check if date is in index or as a column
    date_in_index = isinstance(result_df.index, pd.DatetimeIndex) or (
        isinstance(result_df.index, pd.MultiIndex) and 
        any(level_name == 'date' for level_name in result_df.index.names)
    )
    
    # If date is in index, reset index to get as column
    original_index = None
    if date_in_index:
        original_index = result_df.index.copy()
        result_df = result_df.reset_index()
    
    # Ensure date column is datetime
    if 'date' in result_df.columns:
        result_df['date'] = pd.to_datetime(result_df['date'])
    else:
        raise ValueError("DataFrame must have a 'date' column or index level")
    
    # Create a date range covering all dates in the crypto data
    min_date = result_df['date'].min()
    max_date = result_df['date'].max()
    all_dates = pd.date_range(start=min_date, end=max_date, freq='D')
    
    # Reindex FF factors to include all dates and forward-fill
    expanded_ff = ff_factors.reindex(
        pd.date_range(
            start=min(min_date, ff_factors.index.min()),
            end=max(max_date, ff_factors.index.max()),
            freq='D'
        )
    ).ffill()
    
    # Reset index for merging
    expanded_ff = expanded_ff.reset_index()
    expanded_ff.columns = ['date'] + list(expanded_ff.columns[1:])
    
    # Merge with crypto data
    merged_df = pd.merge(result_df, expanded_ff, on='date', how='left')
    
    # Restore original index structure if needed
    if original_index is not None:
        if isinstance(original_index, pd.MultiIndex):
            # Get the names of the index levels
            index_names = original_index.names
            merged_df = merged_df.set_index(index_names)
        else:
            merged_df = merged_df.set_index(original_index.name)
    
    return merged_df
```


## `replication/Data/data_codes/data_cleaning.py`

Sample filters: zero/negative price drops, return guards ($-100\%$ / $+150\%$), ticker screens, winsorisation.

```python
"""Crypto panel cleaning stage.

Reference
---------
Babiak M, Bianchi D. Mispricing and Risk Compensation in Cryptocurrency Returns.
Journal of Financial and Quantitative Analysis. Published online 2025:1-27.
doi:10.1017/S0022109025102329

Overview
--------
This script:
- removes invalid price observations (close <= 0)
- computes per-asset daily log returns
- winsorizes extreme log returns (user-configurable bounds)
- filters out assets with excessive missing volume data (user-configurable)

Conventions
-----------
- This script does *not* impute missing volume values.
- The volume filter works on NaN-missingness of volumeto (not on zeros). If
  your data encodes missing volume as 0, consider converting 0 -> NaN before
  filtering.
- Optional asset screens can be enabled to remove tickers matching common
  unwanted patterns (e.g., leveraged tokens, fiat/stable tickers) and a small
  list of known problematic symbols.

Inputs
------
A CSV file with at least:
- date   : daily date (parseable by pandas)
- ticker : asset identifier
- close  : closing price (used to compute log returns)
- volumeto : trading volume in quote currency (used for missingness filter)

Outputs
-------
- Cleaned CSV (default): crypto_data_cleaned.csv
  Contains the original columns plus:
    - logret_raw : per-asset daily log return computed from close
    - logret     : winsorized log return used downstream (data_builder expects 'logret')

Usage
-----
Use latest extractor output in the same directory:
  python3 data_cleaning.py

Specify input explicitly:
  python3 data_cleaning.py --input crypto_data_complete_20250403_222225.csv

Write a custom output path:
  python3 data_cleaning.py --output crypto_data_cleaned.csv

"""

import pandas as pd
import numpy as np
from tqdm import tqdm
import logging
import os
import argparse
import glob


# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger()


BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def find_input_file(preferred: str, pattern: str = 'crypto_data_complete_*.csv') -> str:
    """Resolve an input file path.

    If preferred is provided and exists (absolute or relative to this script), use it.
    Otherwise, select the most recent file matching pattern in this directory.
    """
    if preferred:
        candidate = preferred if os.path.isabs(preferred) else os.path.join(BASE_DIR, preferred)
        if os.path.exists(candidate):
            return candidate

    candidates = glob.glob(os.path.join(BASE_DIR, pattern))
    if not candidates:
        raise FileNotFoundError(f"No input files found. Looked for {pattern} in {BASE_DIR}.")

    candidates.sort(key=os.path.getmtime)
    return candidates[-1]


def load_dataset(file_path):
    """Load and prepare the cryptocurrency dataset with proper date/ticker handling."""
    logger.info(f"Loading dataset from {file_path}")

    df = pd.read_csv(file_path)

    if 'date' in df.columns and 'ticker' in df.columns:
        dt = pd.to_datetime(df['date'], errors='coerce', dayfirst=True)
        if dt.isna().mean() > 0.5:
            dt = pd.to_datetime(df['date'], errors='coerce')
        df['date'] = dt
        df = df.dropna(subset=['date'])

        # Standardize ticker (strip whitespace, ensure string)
        df['ticker'] = df['ticker'].astype(str).str.strip()

        logger.info(f"Loaded dataset with {len(df)} rows and {df['ticker'].nunique()} cryptocurrencies")
        return df

    logger.error("Dataset does not have the expected 'date' and 'ticker' columns")
    return None


def apply_default_asset_screens(df: pd.DataFrame) -> pd.DataFrame:
    """Asset screening (wrapped/stable/synthetic) based on ticker heuristics.

    Notes
    -----
    This is still heuristic (ticker-string based), but is implemented to reduce
    false positives versus naive substring filters.

    Rules
    -----
    1) Stable/fiat-like tickers (exact match), e.g. USDT/USDC/BUSD.
    2) Leveraged token patterns commonly used by exchanges, e.g. *BULL, *BEAR,
       *UP, *DOWN as suffixes, plus numeric leverage suffixes (e.g., 3L/3S).
    3) Wrapped tokens: explicit (curated) list of common wrapped tickers.
    4) A small legacy list of specific tickers historically treated as problematic.

    Important
    ---------
    If you have a curated exclusion list from the paper replication, prefer that
    over heuristics.
    """
    if 'ticker' not in df.columns:
        return df

    s = df['ticker'].astype(str).str.strip().str.upper()

    # (1) Exact stable/fiat-like tickers
    stable_exact = {
        # USD-pegged / fiat-like
        'USD', 'USDT', 'USDC', 'BUSD', 'TUSD', 'USDP', 'GUSD', 'USDD',
        # Common EUR/GBP stables
        'EURT', 'EURS', 'GBPT',
        # Metals / asset-backed often treated as non-crypto exposures
        'DGX',
        # Maker stables (legacy)
        'DAI', 'SAI',
    }
    mask_stable_exact = s.isin(stable_exact)

    # (2) Leveraged token naming conventions: suffix-based
    # Examples: BTCUP, BTCDOWN, ETHBULL, ETHBEAR, ETH3L, BTC3S, XRP5L
    mask_leverage = s.str.contains(r'(BULL|BEAR|UP|DOWN|[235]L|[235]S)$', regex=True, na=False)

    # (3) Wrapped tokens: explicit list (avoid broad ^W... regex which can drop valid tickers like WAVES)
    wrapped_exact = {
        'WBTC', 'WETH', 'WBNB', 'WMATIC', 'WAVAX', 'WFTM', 'WONE', 'WCELO',
        'WGLMR', 'WROSE', 'WSTETH',
    }
    mask_wrapped = s.isin(wrapped_exact)

    # Legacy exact exclusions
    drop_exact = {
        'YAM',
        'HPT',
        'BRD',
        'PICKLE',
        'SMT',
        'BOT',
        'ATM',
    }
    mask_exact = s.isin(drop_exact)

    drop_mask = mask_stable_exact | mask_leverage | mask_wrapped | mask_exact

    dropped = s[drop_mask].unique().tolist()
    if dropped:
        sample = dropped[:25]
        logger.info(f"Asset screens: dropping {len(dropped)} tickers (sample: {sample})")

    return df.loc[~drop_mask].copy()


def prepare_returns_and_filter_volume(df, lower_bound=-1.0, upper_bound=1.5):
    """Calculate log returns, winsorize, and filter tickers by missing volume share.

    Notes
    -----
    - Produces both 'logret_raw' and 'logret' (winsorized) to match the naming
      convention used downstream by data_builder.py.
    """
    print("Processing returns and filtering by volume data...")

    processed_df = df.copy()

    if 'close' not in processed_df.columns:
        raise ValueError("Input must include 'close' column")
    if 'volumeto' not in processed_df.columns:
        raise ValueError("Input must include 'volumeto' column")

    initial_rows = len(processed_df)
    processed_df = processed_df[processed_df['close'] > 0]
    rows_dropped_price = initial_rows - len(processed_df)
    print(f"Dropped {rows_dropped_price} rows with zero or negative prices")

    processed_df = processed_df.sort_values(['ticker', 'date'])

    processed_df['logret_raw'] = processed_df.groupby('ticker')['close'].transform(lambda s: np.log(s).diff())

    before_nan_drop = len(processed_df)
    processed_df = processed_df.dropna(subset=['logret_raw'])
    rows_dropped_nan = before_nan_drop - len(processed_df)
    print(f"Dropped {rows_dropped_nan} rows with NaN returns")

    # Winsorized return used downstream
    processed_df['logret'] = processed_df['logret_raw'].clip(lower=lower_bound, upper=upper_bound)

    filtered_df = processed_df

    print(f"Original dataset: {len(df)} rows, {df['ticker'].nunique()} cryptocurrencies")
    print(f"After processing: {len(processed_df)} rows, {processed_df['ticker'].nunique()} cryptocurrencies")
    print(f"Final filtered dataset: {len(filtered_df)} rows, {filtered_df['ticker'].nunique()} cryptocurrencies")

    return filtered_df


def main():
    parser = argparse.ArgumentParser(description='Clean crypto panel (returns + volume-missingness filter).')
    parser.add_argument('--input', default='', help='Input CSV path (or leave empty to use latest synthetic_raw_data.csv)')
    parser.add_argument('--pattern', default='synthetic_raw_data.csv', help='Glob pattern used when --input is empty')
    parser.add_argument('--output', default='crypto_data_cleaned.csv', help='Output cleaned CSV filename/path')
    parser.add_argument('--lower-bound', type=float, default=-1.0, help='Winsorization lower bound for log returns')
    parser.add_argument('--upper-bound', type=float, default=1.5, help='Winsorization upper bound for log returns')
    parser.add_argument('--volume-threshold', type=float, default=0.7, help='Max allowed missing volumeto share per ticker')
    parser.add_argument('--asset-screens', action='store_true', help='Apply heuristic ticker-based asset exclusion screens')
    args = parser.parse_args()

    input_path = find_input_file(args.input, pattern=args.pattern)
    df = load_dataset(input_path)
    if df is None:
        raise SystemExit("Failed to load dataset")

    if args.asset_screens:
        df = apply_default_asset_screens(df)

    df = prepare_returns_and_filter_volume(
        df,
        lower_bound=args.lower_bound,
        upper_bound=args.upper_bound,
    )

    # Ensure canonical sort order for downstream groupby/rolling operations
    df = df.sort_values(['ticker', 'date'])

    out_path = args.output if os.path.isabs(args.output) else os.path.join(BASE_DIR, args.output)
    logger.info(f"Saving filtered dataset to {out_path}")
    df.to_csv(out_path, index=False)


if __name__ == '__main__':
    main()
```


## `replication/Data/data_codes/data_builder.py`

Assembles the cleaned cross-sectional panel and merges Fama-French factors. Drives the order the characteristic functions run in.

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Final dataset builder (fixed).

Reference
---------
Babiak M, Bianchi D. Mispricing and Risk Compensation in Cryptocurrency Returns.
Journal of Financial and Quantitative Analysis. Published online 2025:1-27.
doi:10.1017/S0022109025102329

Overview
--------
This script constructs the characteristic panel used in the empirical analysis.
It is a safer, reproducible replacement for FinalData.py.

Pipeline position
-----------------
- Upstream: Data_clean.py (or equivalent) produces daily raw panels named like
  crypto_data_complete_YYYYMMDD_HHMMSS.csv.
- This script loads those outputs (default input glob: crypto_data_complete_*.csv),
  constructs returns if needed, and computes characteristics using characteristics.py.

Fama-French factors (optional)
------------------------------
Equity-factor merging is optional and requires the user to supply their own
Fama-French factors file via --ff. If --ff is not provided (default), the script
only produces the crypto-only characteristics dataset.

Outputs
-------
- <input>_with_chars.csv
- <input>_with_chars_merged_ff.csv (only when --ff is provided)

Usage
-----
  python3 FinalData_fixed.py
  python3 FinalData_fixed.py --input crypto_data_complete_*.csv --auto-output
  python3 FinalData_fixed.py --ff /path/to/FF_factors.csv

"""

import os
import glob
import argparse
import logging
import sys

import numpy as np
import pandas as pd
from tqdm import tqdm
from data_chrs import *

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def find_input_file(preferred: str, pattern: str = '*.csv') -> str:
    """Resolve input path:
    - If preferred exists (absolute or relative to script dir), use it
    - Else pick the newest matching CSV in script dir or its parent
    """
    if preferred:
        candidate = preferred if os.path.isabs(preferred) else os.path.join(BASE_DIR, preferred)
        if os.path.exists(candidate):
            return candidate

    candidates = glob.glob(os.path.join(BASE_DIR, pattern))
    candidates += glob.glob(os.path.join(os.path.dirname(BASE_DIR), pattern))
    if not candidates:
        raise FileNotFoundError(
            f"Could not find input '{preferred}'. Searched {BASE_DIR} and its parent for {pattern}."
        )

    candidates.sort(key=os.path.getmtime)
    chosen = candidates[-1]
    logger.info(f"Input not found: {preferred}. Using latest CSV: {os.path.basename(chosen)}")
    return chosen

def load_dataset(file_path: str) -> pd.DataFrame:
    """Load and prepare the cryptocurrency dataset with robust date handling."""
    logger.info(f"Loading dataset from {file_path}")

    df = pd.read_csv(file_path)
    if 'date' not in df.columns or 'ticker' not in df.columns:
        raise ValueError("Dataset must include 'date' and 'ticker' columns")

    # Robust parse: dayfirst first, then fallback
    dt = pd.to_datetime(df['date'], errors='coerce', dayfirst=True)
    if dt.isna().mean() > 0.5:
        dt = pd.to_datetime(df['date'], errors='coerce')
    df['date'] = dt
    df = df.dropna(subset=['date'])

    df['ticker'] = df['ticker'].astype(str).str.strip()

    logger.info(f"Loaded {len(df)} rows for {df['ticker'].nunique()} cryptocurrencies")
    return df


def ensure_log_returns(df: pd.DataFrame, price_col: str = 'close', return_col: str = 'logret') -> pd.DataFrame:
    """Ensure log returns exist; compute if missing."""
    if return_col in df.columns:
        return df

    if price_col not in df.columns:
        raise ValueError(
            f"Missing '{return_col}' and cannot compute it because '{price_col}' is not present."
        )

    df = df.copy()
    # Avoid invalid log
    df.loc[df[price_col] <= 0, price_col] = np.nan

    # Compute per ticker
    df = df.sort_values(['ticker', 'date'])
    df[return_col] = df.groupby('ticker')[price_col].transform(lambda s: np.log(s).diff())

    return df


def safe_drop(df: pd.DataFrame, cols) -> pd.DataFrame:
    cols = [c for c in cols if c in df.columns]
    if cols:
        df = df.drop(cols, axis=1)
    return df


def check_missingness(df: pd.DataFrame, by_ticker: bool = False, verbose: bool = True):
    total_obs = len(df)
    if verbose:
        print(f"Total observations: {total_obs}")

    missingness_report = pd.DataFrame({
        'missing_count': df.isna().sum(),
        'missing_percentage': df.isna().mean() * 100,
    }).sort_values('missing_percentage', ascending=False)

    if verbose:
        print("\nOverall Missingness Report:")
        print(missingness_report)

    if by_ticker:
        if not isinstance(df.index, pd.MultiIndex) or 'ticker' not in df.index.names:
            raise ValueError("by_ticker=True requires a MultiIndex with level 'ticker'")

        ticker_missingness = (
            df.reset_index()
            .groupby('ticker')
            .apply(lambda g: (g.isna().mean() * 100))
        )
        return missingness_report, ticker_missingness

    return missingness_report


def check_average_missingness_by_crypto(df: pd.DataFrame) -> pd.DataFrame:
    if not isinstance(df.index, pd.MultiIndex) or 'ticker' not in df.index.names:
        raise ValueError("DataFrame index must contain 'ticker' level")

    tickers = df.index.get_level_values('ticker').unique()
    num_tickers = len(tickers)
    logger.info(f"Analyzing missingness across {num_tickers} cryptocurrencies")

    per_ticker = []
    for ticker in tqdm(tickers, desc="Processing cryptocurrencies"):
        td = df.xs(ticker, level='ticker')
        per_ticker.append(td.isna().mean() * 100)

    avg = pd.concat(per_ticker, axis=1).mean(axis=1)
    report = pd.DataFrame({'avg_missing_percentage': avg}).sort_values('avg_missing_percentage', ascending=False)
    return report


def prepare_and_merge_ff_factors(crypto_df: pd.DataFrame, ff_csv_path: str) -> pd.DataFrame:
    ff_factors = pd.read_csv(ff_csv_path)
    if 'date' not in ff_factors.columns:
        raise ValueError("FF factors CSV must include 'date' column")

    # Expect YYYYMMDD
    ff_factors['date'] = pd.to_datetime(ff_factors['date'], format='%Y%m%d', errors='coerce')
    ff_factors = ff_factors.dropna(subset=['date']).set_index('date')

    ff_factors = ff_factors.rename(columns={
        'Mkt-RF': 'market_excess_return',
        'SMB': 'size_factor',
        'HML': 'value_factor',
        'RMW': 'profitability_factor',
        'CMA': 'investment_factor',
        'RF': 'risk_free_rate',
    })

    if 'market_excess_return' in ff_factors.columns and 'risk_free_rate' in ff_factors.columns:
        ff_factors['market_return'] = ff_factors['market_excess_return'] + ff_factors['risk_free_rate']

    # Work in columns
    original_index = crypto_df.index
    df = crypto_df.reset_index() if isinstance(original_index, pd.MultiIndex) else crypto_df.copy()

    if 'date' not in df.columns:
        raise ValueError("crypto_df must have 'date' as a column or index level")

    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df = df.dropna(subset=['date'])

    expanded_ff = ff_factors.reindex(
        pd.date_range(
            start=min(df['date'].min(), ff_factors.index.min()),
            end=max(df['date'].max(), ff_factors.index.max()),
            freq='D',
        )
    ).ffill().reset_index().rename(columns={'index': 'date'})

    merged = pd.merge(df, expanded_ff, on='date', how='left')

    if isinstance(original_index, pd.MultiIndex):
        merged = merged.set_index(list(original_index.names))

    return merged


def build_characteristics(df: pd.DataFrame) -> pd.DataFrame:
    """Compute characteristics, mirroring FinalData.py but fixing common failure points."""

    # Ensure returns exist for all downstream metrics
    df = ensure_log_returns(df, price_col='close', return_col='logret')

    # Use MultiIndex
    df = df.set_index(['ticker', 'date']).sort_index()

    # 1 Amihud illiquidity
    df['ahcc30'] = df.groupby(level='ticker', group_keys=False).apply(lambda x: amihud_illiquidity(x))

    # 2 Bid-ask spread
    df['cs_spread'] = corwin_schultz(df)
    df['ar_spread'] = abdi_ranaldo(df)
    df['bidask'] = (df['cs_spread'] + df['ar_spread']) / 4
    df = safe_drop(df, ['cs_spread', 'ar_spread'])

    # 3 Volume shocks 
    df = calculate_volume_shocks(df, window_lengths=[30])

    # 4 Size (log market cap)
    if 'marketcap' not in df.columns:
        if 'close' in df.columns and 'current_supply' in df.columns:
            df['marketcap'] = df['close'] * df['current_supply']
        else:
            df['marketcap'] = np.nan

    df['marketcap'] = df['marketcap'].replace([0, np.inf, -np.inf], np.nan)
    df['size'] = np.log(df['marketcap'])

    # 5-7 market alpha, beta, idio vol vs crypto market index 
    df = calculate_value_weighted_index(df)
    df = calculate_market_betas(df, window=60, min_periods=30)

    # 8 short-term reversal
    df['r2_1'] = df.groupby(level='ticker')['logret'].shift(1)

    # 9-14 Momentum
    df = calculate_momentum(df, lookback_periods=[7, 14, 21, 30], custom_periods=[(30, 14), (180, 60)])

    # 15-16 MAX and MAX(N) 
    df = calculate_max_return(df, window=30, top_n_avg=4)

    # 17 Relative-to-high
    df = calculate_relative_to_high(df, window=90)

    # 18 book-to-market proxy
    df = calculate_crypto_book_to_market(df, addresses_col='unique_addresses_all_time', market_cap_col='marketcap')

    # 19 Turnover
    if 'volumeto' in df.columns:
        df['volume'] = df['volumeto']   # alias expected by downstream analysis
        df['turnover'] = df['volumeto'] / df['marketcap']
    else:
        df['volume'] = np.nan
        df['turnover'] = np.nan

    # 20-21 volume-based measures 
    df = calculate_volatility_metrics(
        df,
        turnover_col='turnover',
        volume_col='volumeto',
        window=30,
        min_periods=15,
        log_transform_volume=True,
    )

    # 22 detrended turnover
    df = calculate_detrended_turnover(
        df,
        volume_col='volumeto',
        market_cap_col='marketcap',
        turnover_col='turnover',
        window=30,
    )

    # 23 volume CV 
    df = calculate_volume_cv(df, volume_col='volumeto', window=30, min_periods=30)

    # 24-25 realized skewness and coskewness vs crypto market 
    df = calculate_realized_skewness(df, return_col='logret', window=30, min_periods=30)
    df = df.rename(columns={'rskew_30': 'rskew'})
    df = calculate_coskewness(df, return_col='logret', market_return_col='vw-index', window=60, min_periods=30)

    # 26 EWMA realized volatility 
    df = calculate_ewma_volatility(df, return_col='logret', lambda_=0.94)
    df = df.rename(columns={'ewma_vol': 'rvol'})

    # 27 VaR
    df = calculate_var(df, return_col='logret', window=90, confidence=0.05, min_periods=30)

    # 28 downside beta vs crypto market 
    df = calculate_downside_beta(df, return_col='logret', market_col='vw-index', window=60, min_periods=15)
    df = df.rename(columns={'downside_beta': 'down_beta'})

    # Rename idio_vol -> ivol for crypto-only output
    df = df.rename(columns={'idio_vol': 'ivol'})

    return df


def apply_paper_missingness_filters(
    df: pd.DataFrame,
    drop_missing_marketcap: bool = False,
    drop_missing_volume: bool = False,
    marketcap_col: str = 'marketcap',
    volume_col: str = 'volumeto',
) -> pd.DataFrame:
    """Optionally drop rows with missing market cap and/or trading volume.

    Notes
    -----
    This is intended to match the paper's description of removing observations
    with missing market capitalization or trading volume. It is applied after
    marketcap has been created (if possible) in build_characteristics().
    """
    out = df

    to_drop = []
    if drop_missing_marketcap and marketcap_col in out.columns:
        to_drop.append(marketcap_col)
    if drop_missing_volume and volume_col in out.columns:
        to_drop.append(volume_col)

    if not to_drop:
        return out

    before = len(out)
    out = out.dropna(subset=to_drop)
    dropped = before - len(out)
    logger.info(f"Dropped {dropped} rows due to missingness in {to_drop}")
    return out


def main():
    parser = argparse.ArgumentParser(description='Build final crypto dataset with characteristics (fixed).')
    parser.add_argument(
        '--input',
        default='crypto_data_cleaned.csv',
        help="Input CSV filename/path or glob (default: 'crypto_data_cleaned.csv')",
    )
    parser.add_argument(
        '--ff',
        default='FF_factors.csv',
        help=(
            "Path to your Fama-French factors CSV (default: 'FF_factors.csv'). "
            "If provided, the script will merge factors and compute equity-exposure characteristics."
        ),
    )
    parser.add_argument('--no-ff-merge', action='store_true', help='Skip FF merge and equity-exposure metrics')
    parser.add_argument('--output', default=None, help='Output CSV for crypto-only characteristics')
    parser.add_argument('--output-merged', default=None, help='Output CSV after FF merge and equity exposures')
    parser.add_argument('--missingness-csv', default=None, help='Optional path to write missingness report (avg across cryptos)')
    parser.add_argument('--auto-output', action='store_true', help='Derive output names from input')

    # Paper-aligned row filters (optional)
    parser.add_argument('--drop-missing-marketcap', action='store_true', help="Drop rows with missing 'marketcap' after it is constructed")
    parser.add_argument('--drop-missing-volume', action='store_true', help="Drop rows with missing 'volumeto'")

    args = parser.parse_args()

    try:
        pattern = args.input if any(ch in args.input for ch in ['*', '?', '[']) else '*.csv'
        input_path = find_input_file(args.input, pattern=pattern)
    except Exception as e:
        logger.error(str(e))
        sys.exit(1)

    df_raw = load_dataset(input_path)

    df_char = build_characteristics(df_raw)

    # Apply paper-aligned missingness filters (if enabled)
    df_char = apply_paper_missingness_filters(
        df_char,
        drop_missing_marketcap=args.drop_missing_marketcap,
        drop_missing_volume=args.drop_missing_volume,
        marketcap_col='marketcap',
        volume_col='volumeto',
    )

    in_base = os.path.splitext(os.path.basename(input_path))[0]
    out_crypto = args.output
    out_merged = args.output_merged

    if args.auto_output or out_crypto is None:
        out_crypto = os.path.join(BASE_DIR, f"{in_base}_with_chars.csv")
    if args.auto_output or out_merged is None:
        out_merged = os.path.join(BASE_DIR, f"{in_base}_with_chars_merged_ff.csv")

    logger.info(f"Saving crypto-only characteristics to {out_crypto}")
    df_char.to_csv(out_crypto, index=True)

    if args.missingness_csv:
        report = check_average_missingness_by_crypto(df_char)
        report.to_csv(args.missingness_csv, index=True)
        logger.info(f"Saved missingness report to {args.missingness_csv}")

    if args.no_ff_merge:
        return

    ff_path = args.ff if os.path.isabs(args.ff) else os.path.join(BASE_DIR, args.ff)
    if not os.path.exists(ff_path):
        logger.error(f"FF factors not found: {ff_path}. Provide --ff PATH or use --no-ff-merge.")
        return

    merged = prepare_and_merge_ff_factors(df_char, ff_path)

    # Equity exposure variables
    # Temporarily rename crypto-market columns that would clash with the equity
    # versions produced below, then restore them afterwards.
    merged = merged.rename(columns={
        'capm_beta':  '_capm_beta_crypto',
        'capm_alpha': '_capm_alpha_crypto',
        'ivol':       '_ivol_crypto',
        'coskew':     '_coskew_crypto',
        'down_beta':  '_down_beta_crypto',
    })

    merged = calculate_market_betas(
        merged,
        return_col='logret',
        market_col='market_excess_return',
        window=60,
        min_periods=30,
    )
    # capm_beta, capm_alpha, idio_vol now hold equity versions → rename immediately
    merged = merged.rename(columns={
        'capm_beta':  'capm_beta_equity',
        'capm_alpha': 'capm_alpha_equity',
        'idio_vol':   'ivol_equity',
    })

    merged = calculate_coskewness(
        merged,
        return_col='logret',
        market_return_col='market_excess_return',
        window=60,
        min_periods=30,
    )
    # coskew now holds equity version → rename immediately
    merged = merged.rename(columns={'coskew': 'coskew_equity'})

    merged = calculate_downside_beta(
        merged,
        return_col='logret',
        market_col='market_excess_return',
        window=60,
        min_periods=15,
    )
    # downside_beta now holds equity version → rename immediately
    merged = merged.rename(columns={'downside_beta': 'down_beta_equity'})

    # Restore crypto-market columns to their clean names (no suffix)
    merged = merged.rename(columns={
        '_capm_beta_crypto':  'capm_beta',
        '_capm_alpha_crypto': 'capm_alpha',
        '_ivol_crypto':       'ivol',
        '_coskew_crypto':     'coskew',
        '_down_beta_crypto':  'down_beta',
    })

    # Drop columns not needed in final output
    merged = safe_drop(
        merged,
        [
            # FF factor columns
            'market_excess_return',
            'size_factor',
            'value_factor',
            'profitability_factor',
            'investment_factor',
            'risk_free_rate',
            'market_return',
            # Equity intermediates not in predvars
            'capm_alpha_equity',
            'ivol_equity',
            # Intermediate/redundant columns
            'capm_alpha',
            'r30_14',
            'size',
            'value-weights-idx',
            'vw-index',
            'market-to',
            'std_to',
            'sq_returns',
            'ewma_var',
        ],
    )

    logger.info(f"Saving merged (FF + equity exposures) dataset to {out_merged}")
    merged.to_csv(out_merged, index=True)


if __name__ == '__main__':
    main()
```


## `replication/Data/data_codes/data_fetch.py`

Downloads OHLCV + social + blockchain metrics from CryptoCompare (and IntoTheBlock via CryptoCompare). Authoritative source for the raw-data step.

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CryptoCompare daily panel extractor.

Reference
---------
Babiak M, Bianchi D. Mispricing and Risk Compensation in Cryptocurrency Returns.
Journal of Financial and Quantitative Analysis. Published online 2025:1-27.
doi:10.1017/S0022109025102329

This script downloads daily cryptocurrency data from the CryptoCompare API and
builds a panel dataset suitable for downstream feature construction.

Data sources (CryptoCompare endpoints)
-------------------------------------
1) Market OHLCV (daily):
   https://min-api.cryptocompare.com/data/v2/histoday

2) Social metrics (daily):
   https://min-api.cryptocompare.com/data/social/coin/histo/day

3) Blockchain metrics (daily):
   https://min-api.cryptocompare.com/data/blockchain/histo/day

4) Universe list (blockchain-enabled coins):
   https://min-api.cryptocompare.com/data/blockchain/list

Notes
-----
- You must provide your own CryptoCompare API key.
- The output CSV is named like: crypto_data_complete_YYYYMMDD_HHMMSS.csv
- Output columns include at minimum: date, ticker, open, high, low, close,
  volumeto, volumefrom, plus any available social/blockchain columns.

Compatibility with FinalData_fixed.py
------------------------------------
FinalData_fixed.py expects at least:
- 'date' column parseable as daily datetime
- 'ticker' column
- 'close' column (to build log returns if 'logret' is absent)
- 'volumeto' and 'current_supply' are used if present

This extractor writes rows with (date, ticker) and keeps these columns when
available.

Usage
-----
Option A (recommended): set API key in environment variable:
  export CRYPTOCOMPARE_API_KEY="..."
  python3 Data_clean.py

Option B: pass API key explicitly:
  python3 Data_clean.py --api-key "..."
  
"""

from __future__ import annotations

import os
import time
import glob
import argparse
import logging
from datetime import datetime
from typing import Any, Dict, Optional, Tuple, List

import requests as req
import pandas as pd


# ----------------------------
# Logging
# ----------------------------
logger = logging.getLogger(__name__)


def setup_logging(log_path: str, verbose: bool = True) -> None:
    handlers: List[logging.Handler] = [logging.FileHandler(log_path)]
    if verbose:
        handlers.append(logging.StreamHandler())

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=handlers,
    )


# ----------------------------
# HTTP helper
# ----------------------------
def fetch_api_data(url: str, max_retries: int = 3, retry_delay: float = 2.0) -> Any:
    """Fetch JSON from URL with small retry/backoff."""
    delay = retry_delay
    last_err: Optional[Exception] = None

    for attempt in range(1, max_retries + 1):
        try:
            response = req.get(url, timeout=60)
            response.raise_for_status()
            return response.json()
        except req.exceptions.RequestException as e:
            last_err = e
            logger.warning(f"API request failed (attempt {attempt}/{max_retries}): {e}")
            if attempt < max_retries:
                logger.info(f"Retrying in {delay:.0f} seconds...")
                time.sleep(delay)
                delay *= 2

    raise RuntimeError(f"Max retries reached for URL: {url}") from last_err


# ----------------------------
# Endpoint wrappers
# ----------------------------
def get_market_data(
    ticker: str,
    tsym: str,
    api_key: str,
    limit: int = 2000,
    to_ts: Optional[int] = None,
) -> Tuple[Optional[pd.DataFrame], Optional[int]]:
    """Fetch daily OHLCV market data for one asset.

    Returns
    -------
    (df, time_from)
      - df: index ['date','ticker'] with columns open/high/low/close/volumeto/volumefrom
      - time_from: earliest timestamp in this batch (seconds since epoch), used to page backward
    """
    base_url = "https://min-api.cryptocompare.com/data/v2/histoday"
    url = (
        f"{base_url}?fsym={ticker}&tsym={tsym}&limit={limit}"
        f"&e=CCCAGG&tryConversion=true&api_key={api_key}"
    )
    if to_ts is not None:
        url += f"&toTs={to_ts}"

    try:
        data = fetch_api_data(url)
        series = data.get('Data', {}).get('Data')
        if not series:
            return None, None

        time_from = data.get('Data', {}).get('TimeFrom')

        df = pd.DataFrame(series)
        df['ticker'] = str(ticker)
        df['date'] = pd.to_datetime(df['time'], unit='s', utc=True).dt.tz_convert(None)
        df = df.drop(columns=[c for c in ['time', 'conversionSymbol', 'conversionType'] if c in df.columns])
        df = df.set_index(['date', 'ticker']).sort_index()

        keep_cols = [c for c in ['open', 'high', 'low', 'close', 'volumeto', 'volumefrom'] if c in df.columns]
        return df[keep_cols], time_from

    except Exception as e:
        logger.error(f"Error fetching market data for {ticker}: {e}")
        return None, None


def get_social_data(
    coin_id: int,
    api_key: str,
    limit: int = 2000,
    to_ts: Optional[int] = None,
) -> Optional[pd.DataFrame]:
    """Fetch daily social data and return indexed by 'date'."""
    base_url = "https://min-api.cryptocompare.com/data/social/coin/histo/day"
    url = f"{base_url}?coinId={coin_id}&limit={limit}&api_key={api_key}"
    if to_ts is not None:
        url += f"&toTs={to_ts}"

    try:
        data = fetch_api_data(url)
        series = data.get('Data', [])
        if not series:
            return None

        rows = []
        for item in series:
            rows.append({
                'date': pd.to_datetime(item['time'], unit='s', utc=True).tz_convert(None),
                'reddit_posts_per_day': item.get('reddit_posts_per_day'),
                'fb_likes': item.get('fb_likes'),
                'fb_talking_about': item.get('fb_talking_about'),
                'twitter_followers': item.get('twitter_followers'),
                'reddit_subscribers': item.get('reddit_subscribers'),
                'reddit_active_users': item.get('reddit_active_users'),
                'code_repo_closed_issues': item.get('code_repo_closed_issues'),
                'code_repo_stars': item.get('code_repo_stars'),
            })

        df = pd.DataFrame(rows).set_index('date').sort_index()
        return df

    except Exception as e:
        logger.error(f"Error fetching social data for coin ID {coin_id}: {e}")
        return None


def get_blockchain_data(
    ticker: str,
    api_key: str,
    limit: int = 2000,
    to_ts: Optional[int] = None,
) -> Optional[pd.DataFrame]:
    """Fetch daily blockchain data for one asset.

    Returns a DataFrame indexed by ['date','ticker'].
    """
    base_url = "https://min-api.cryptocompare.com/data/blockchain/histo/day"
    url = f"{base_url}?fsym={ticker}&limit={limit}&api_key={api_key}"
    if to_ts is not None:
        url += f"&toTs={to_ts}"

    try:
        data = fetch_api_data(url)
        series = data.get('Data', {}).get('Data', [])
        if not series:
            return None

        df = pd.DataFrame(series)
        df['date'] = pd.to_datetime(df['time'], unit='s', utc=True).dt.tz_convert(None)
        df = df.drop(columns=[c for c in ['time', 'id'] if c in df.columns])

        # CryptoCompare returns "symbol"; normalize to "ticker"
        if 'symbol' in df.columns:
            df = df.rename(columns={'symbol': 'ticker'})
        else:
            df['ticker'] = ticker

        df['ticker'] = df['ticker'].astype(str)
        df = df.set_index(['date', 'ticker']).sort_index()
        return df

    except Exception as e:
        logger.error(f"Error fetching blockchain data for {ticker}: {e}")
        return None


# ----------------------------
# Asset batching
# ----------------------------
SOCIAL_COLUMNS = [
    'reddit_posts_per_day',
    'fb_likes',
    'fb_talking_about',
    'twitter_followers',
    'reddit_subscribers',
    'reddit_active_users',
    'code_repo_closed_issues',
    'code_repo_stars',
]

BLOCKCHAIN_COLUMNS = [
    'active_addresses',
    'average_transaction_value',
    'block_height',
    'block_size',
    'block_time',
    'current_supply',
    'difficulty',
    'hashrate',
    'large_transaction_count',
    'new_addresses',
    'transaction_count',
    'transaction_count_all_time',
    'unique_addresses_all_time',
    'zero_balance_addresses_all_time',
]


def fetch_historical_data(
    ticker: str,
    coin_id: int,
    api_key: str,
    tsym: str = 'USD',
    max_batches: int = 2,
    limit: int = 2000,
    sleep_between_batches: float = 1.0,
) -> Optional[pd.DataFrame]:
    """Fetch multiple backward pages of data for one asset and merge market/social/blockchain."""

    complete = []
    current_to_ts: Optional[int] = None

    for batch in range(1, max_batches + 1):
        logger.info(f"{ticker}: fetching batch {batch}/{max_batches}")

        market_df, time_from = get_market_data(ticker, tsym, api_key, limit=limit, to_ts=current_to_ts)
        if market_df is None or market_df.empty:
            break

        social_df = get_social_data(coin_id, api_key, limit=limit, to_ts=current_to_ts)
        if social_df is None:
            social_df = pd.DataFrame(index=market_df.index.get_level_values('date').unique(), columns=SOCIAL_COLUMNS)
            social_df.index.name = 'date'

        # left join: preserve all market dates
        combined = market_df.merge(social_df, how='left', left_index=True, right_index=True)

        bc_df = get_blockchain_data(ticker, api_key, limit=limit, to_ts=current_to_ts)
        if bc_df is None:
            idx = pd.MultiIndex.from_product(
                [combined.index.get_level_values('date').unique(), [ticker]],
                names=['date', 'ticker'],
            )
            bc_df = pd.DataFrame(index=idx, columns=BLOCKCHAIN_COLUMNS)

        batch_df = combined.merge(bc_df, how='left', left_index=True, right_index=True)
        complete.append(batch_df)

        current_to_ts = time_from
        if current_to_ts is None:
            break

        time.sleep(sleep_between_batches)

    if not complete:
        return None

    out = pd.concat(complete, axis=0)
    out = out.sort_index(level='date')
    out = out[~out.index.duplicated(keep='first')]
    return out


# ----------------------------
# Universe
# ----------------------------
def get_universe(api_key: str) -> Dict[str, Dict[str, Any]]:
    """Return mapping ticker -> metadata for coins with blockchain data."""
    url = f"https://min-api.cryptocompare.com/data/blockchain/list?api_key={api_key}"
    data = fetch_api_data(url)
    universe = data.get('Data')
    if not isinstance(universe, dict):
        raise RuntimeError("Unexpected response format when fetching universe")
    return universe


# ----------------------------
# Main
# ----------------------------
def main() -> None:
    parser = argparse.ArgumentParser(description='Extract CryptoCompare daily panel data (clean).')
    parser.add_argument('--api-key', default=os.getenv('CRYPTOCOMPARE_API_KEY', ''), help='CryptoCompare API key (or set CRYPTOCOMPARE_API_KEY)')
    parser.add_argument('--tsym', default='USD', help='Quote currency (default: USD)')
    parser.add_argument('--max-batches', type=int, default=2, help='How many backward pages to request per asset (default: 2)')
    parser.add_argument('--limit', type=int, default=2000, help='API limit per request (default: 2000)')
    parser.add_argument('--save-interval', type=int, default=30, help='Save partial CSV every N tickers (default: 30)')
    parser.add_argument('--rate-limit-pause-every', type=int, default=5, help='Pause every N tickers to reduce rate limiting (default: 5)')
    parser.add_argument('--rate-limit-pause-seconds', type=float, default=3.0, help='Seconds to pause for rate limiting (default: 3)')
    parser.add_argument('--log', default='crypto_extraction.log', help='Log filename (default: crypto_extraction.log)')
    parser.add_argument('--output-dir', default='.', help='Output directory (default: current directory)')
    parser.add_argument('--verbose', action='store_true', help='Also log to stdout')
    args = parser.parse_args()

    setup_logging(args.log, verbose=args.verbose)

    if not args.api_key:
        raise SystemExit("Missing API key. Provide --api-key or set CRYPTOCOMPARE_API_KEY.")

    output_dir = args.output_dir
    if not os.path.isabs(output_dir):
        output_dir = os.path.abspath(output_dir)
    os.makedirs(output_dir, exist_ok=True)

    universe = get_universe(args.api_key)
    tickers = list(universe.keys())
    logger.info(f"Universe size (blockchain-enabled): {len(tickers)}")

    all_data = []
    processed = 0

    for i, ticker in enumerate(tickers, start=1):
        try:
            if i > 1 and args.rate_limit_pause_every > 0 and i % args.rate_limit_pause_every == 0:
                logger.info("Rate limit pause...")
                time.sleep(args.rate_limit_pause_seconds)

            meta = universe.get(ticker, {})
            coin_id = meta.get('id')
            if not coin_id:
                logger.warning(f"{ticker}: missing coin id; skipping")
                continue

            logger.info(f"Processing {ticker} ({i}/{len(tickers)})")
            df_t = fetch_historical_data(
                ticker=ticker,
                coin_id=int(coin_id),
                api_key=args.api_key,
                tsym=args.tsym,
                max_batches=args.max_batches,
                limit=args.limit,
            )

            if df_t is None or df_t.empty:
                logger.info(f"{ticker}: no data")
                continue

            all_data.append(df_t)
            processed += 1
            logger.info(f"{ticker}: collected {len(df_t)} rows")

            if args.save_interval > 0 and processed % args.save_interval == 0:
                partial_path = os.path.join(output_dir, f"crypto_data_partial_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
                pd.concat(all_data, axis=0).to_csv(partial_path)
                logger.info(f"Saved partial dataset: {partial_path}")

        except Exception as e:
            logger.error(f"{ticker}: unexpected failure: {e}")
            continue

    if not all_data:
        logger.warning("No data collected for any cryptocurrency")
        return

    final_df = pd.concat(all_data, axis=0)
    final_df = final_df.sort_index(level='date')

    final_path = os.path.join(output_dir, f"crypto_data_complete_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
    final_df.to_csv(final_path)

    logger.info(f"Extraction complete. Assets processed: {processed}/{len(tickers)}")
    logger.info(f"Final dataset shape: {final_df.shape}")
    logger.info(f"Saved: {final_path}")


if __name__ == '__main__':
    main()
```


## `replication/README.md`

Maps every empirical script in `CODE/` (one per figure/table) to the output it produces. The empirical scripts themselves are not bundled; this README is enough to tell the reader which file to open on Dataverse.

```markdown
# Replication Material for: Babiak M, Bianchi D. *Mispricing and Risk Compensation in Cryptocurrency Returns*. Journal of Financial and Quantitative Analysis. Published online 2025:1–27. doi:10.1017/S0022109025102329

# Description:

This replication package provides the simulated data and code required to reproduce the tables and figures in the paper's main text (Figures 5 and 6, and Table 8, which are trivial full-sample and rolling-window regressions, are omitted).

Please ensure that the required data files are in the Data folder (the synthetic data has already been copied for convenience) and run the scripts in the CODE folder. Enjoy! :)

## The `DATA` folder contains:

- data_cs.csv: Dummy data for the panel of cryptocurrency returns generated synthetically.
- FF_factors.csv: The time series for the Fama-French factors from the Ken French library.
- riskfactors_pca.csv: The synthetic PCA factors. 
- riskfactors.csv: The synthetic observable factors. 
- DATA_CODES contains all the routines needed to reconstruct the data starting from a CryptoCompare API key (which the user is assumed to have):
	a. `data_fetch.py`: download daily OHLCV + social + blockchain metrics from CryptoCompare (and IntoTheBlock via CryptoCompare).
	b. `data_cleaning.py`: drop invalid prices, compute `logret`, winsorize, apply ticker screens.
	c. `data_builder.py`: compute characteristics using `data_chrs.py`; optionally drop rows with missing `marketcap`/`volumeto`; optionally merge FF factors.
	d. `data_chrs.py`: characteristic construction functions (liquidity, trading activity, momentum/reversal, risk and exposures).

## The `CODE` folder contains scripts used to generate the empirical results (figures/tables):

### Figures
- `Figure_1_2_All_Char.py`: rolling-window IPCA bootstrap W-alpha (all characteristics).
- `Figure_1_2_Group_Char.py`: rolling-window IPCA bootstrap W-alpha for grouped characteristics.
- `Figure_3_4_Groups_Char.py`: rolling-window IPCA bootstrap W-beta for grouped characteristics.

### Tables (IPCA)
- `Table_2_IPCA.py`: in-sample IPCA estimation (restricted/unrestricted), factors/gammas, fitted values, and Table 2 outputs.
- `Table_2_IPCA_Restr_OOS.py`: out-of-sample IPCA (restricted) goodness-of-fit.
- `Table_2_3_IPCA_Unrestr_OOS.py`: out-of-sample IPCA (unrestricted) goodness-of-fit and alpha-portfolio stats in Table 3.

### Tables (observable factor models)
- `Table_2_Obs.py`: in-sample observable factor benchmarks (restricted/unrestricted) with IPCA-style instruments.
- `Table_2_Obs_OOS.py`: out-of-sample observable factor benchmarks (restricted/unrestricted).

### Tables (PCA benchmark)
- `Table_2_PCA.py`: in-sample PCA-factor benchmark (restricted).
- `Table_2_PCA_OOS.py`: out-of-sample PCA-factor benchmark (restricted).

### Bootstrap summary logs
- `Table_4_All_Char.py`: bootstrap W-alpha (all characteristics).
- `Table_4_Group_Char.py`: bootstrap W-alpha (grouped characteristics).
- `Table_5_Group_Char.py`: bootstrap W-beta (grouped characteristics).

### MATLAB utility
- `Table_6.m`: loads fitted values and computes R² by characteristic-sorted bins.

### Bootstrap summary logs
- `Table_7_indiv.py`: bootstrap W-delta for significance of the Fama-French factors (estimated individually).
- `Table_7_joint.py`: bootstrap W-delta for significance of the Fama-French factors (estimated jointly).

Dependencies include `pandas`, `numpy`, `scikit-learn`, `statsmodels` (some scripts), `joblib` (some scripts), and the local `ipca_prop` module.

## The `R2_Comparison` folder
- `R2_comparison.m`: compares forecasting performance between the two models based on their fitted values

## The `RESULTS` folder contains the subfolder where the results and estimation outputs are saved
```
