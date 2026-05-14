# Mispricing and Risk Compensation in Cryptocurrency Returns

_Mykola Babiak and Daniele Bianchi_

**Journal of Financial and Quantitative Analysis**, 2026 (published online 2025). DOI: [10.1017/S0022109025102329](https://doi.org/10.1017/S0022109025102329). Replication: [Harvard Dataverse](https://doi.org/10.7910/DVN/IQR5DH).

## Abstract

We examine the role of systematic mispricing and risk compensation in explaining cryptocurrency returns using instrumented principal component analysis. We demonstrate that both elements make meaningful contributions to the variation in returns through distinct economic mechanisms. Mispricing primarily operates through behavioral channels, capturing speculative demand and liquidity frictions. A pure-alpha strategy delivers large and significant Sharpe ratios, confirming the economic importance of mispricing. Risk compensation is driven by fundamental factors, including past performance and exposures to both cryptocurrency and equity market risk. Consistent with this equity exposure, we document increasing correlation between cryptocurrency and equity returns over time.


# Introduction

A central question in empirical asset pricing is to what extent the variation in asset returns is driven by exposure to common risk factors and to what extent by a mispricing component. This distinction is not merely statistical; it reflects the fundamental economic forces at work. Traditional asset pricing theory posits that mispricing is idiosyncratic and transient, quickly eliminated by arbitrageurs, leaving risk compensation as the sole determinant of return variation. However, when arbitrage is costly or limited, predictable return variation that is unrelated to common factors can emerge (Stambaugh and Yuan, 2017).

Cryptocurrency markets present a particularly compelling setting for this analysis. On the one hand, Makarov and Schoar (2020) show how trading fragmentation and frictions, limited arbitrage capital, and heterogeneous investor bases—ranging from sophisticated institutions to retail speculators—generate persistent mispricing that arbitrageurs cannot efficiently eliminate. On the other hand, cryptocurrencies exhibit systematic return patterns related to common factors, such as size and momentum (Liu et al., 2022), suggesting that risk-based explanations of return predictability retain relevance.

We investigate this tension by leveraging the flexibility of instrumented principal component analysis (IPCA) – a conditional latent factor model where alphas and betas are explicitly linked to asset characteristics (Kelly et al., 2019). IPCA is particularly suited for our analysis because it allows us to directly assess the extent to which systematic mispricing can explain the variation in expected returns conditional on common factor components. (footnote: Conventional static factor models are often not designed to accommodate systematic mispricing, as their primary focus is on modeling comovements (Chen et al., 2023).) We refer to Giglio et al. (2022) for a complete review of factor models in asset pricing.

Crucially, within the IPCA framework, asset characteristics can be associated with systematic mispricing, risk compensation, or both. If a characteristic significantly affects conditional alphas, it indicates predictable mispricing related to fundamental asset properties. Conversely, if a characteristic affects conditional betas, it signals a role in determining time-varying exposures to common risk factors. This distinction is key to our contribution, as it allows us to empirically quantify which characteristics primarily drive mispricing and which drive risk compensation.

Using an unbalanced panel of over 600 cryptocurrencies from September 2017 to May 2023, we document three main findings that directly address the relative importance of systematic mispricing versus risk compensation in cryptocurrency returns. First, we establish that systematic mispricing and time-varying risk compensation play distinct but complementary roles in cryptocurrency markets. Systematic mispricing represents a substantial source of predictable return variation that operates independently of factor structure. Alphas conditioning on speculative demand, liquidity, and reversal remain strongly significant even after including up to eight latent factors. Furthermore, allowing for systematic mispricing substantially improves the model's predictive $R^2$ compared to specifications that restrict mispricing to zero. This improvement holds across latent IPCA factors, observable factors, and characteristic-managed portfolios. Pure-alpha portfolios generate economically and statistically significant returns that systematic factors cannot explain, demonstrating that mispricing represents genuine economic value rather than a statistical artifact.

Second, we quantify the relative contributions of different characteristics to mispricing and risk compensation. Recursive bootstrap tests reveal that speculative demand represents the most significant contributor to pricing inefficiencies throughout the sample, with this contribution intensifying during market run-ups. This suggests investors associate cryptocurrencies with lottery-like assets. Liquidity and volatility-related variables provide additional explanatory power for mispricing, while reversal characteristics become the primary drivers of weekly alphas. In contrast, core attributes---market exposure, size, and past performance---represent the most robust determinants of conditional betas for both daily and weekly returns. This quantitative decomposition demonstrates that both systematic mispricing and risk compensation play economically meaningful but distinct roles.

Third, we demonstrate that the risk compensation component is increasingly reflecting exposure to broader equity market factors rather than cryptocurrency-specific risks. Characteristics capturing individual cryptocurrency exposure to equity market returns significantly drive conditional betas, challenging conventional views on market segmentation (Liu and Tsyvinski, 2021). A simple spanning regression analysis supports this integration by showing that IPCA latent factors exhibit significant correlations with equity market factors, with these correlations increasing over time. This pattern is consistent with Pástor and Veronesi (2009): as investors and institutions gain more exposure to innovative sectors, information asymmetry and cross-market barriers diminish, leading to increased risk spillovers.

Our work is related to a growing body of literature that aims to understand the determinants of cryptocurrency returns. Following the blueprint proposed by Fama and French (1993) for equities, Liu et al. (2022) and Cong et al. (2021) suggest a series of long-short portfolios based on cryptocurrency characteristics such as market capitalization, network growth, or past returns, to elucidate beta pricing relationships. In contrast, Borri et al. (2022) assume that risk factors are latent. However, these approaches share a common limitation: they assume that mispricing is either absent or akin to an idiosyncratic error term, rather than recognizing it as an economically significant and systematic determinant of expected returns. This assumption may be particularly problematic for cryptocurrency markets where systematic mispricing may be endemic rather than transitory (Makarov and Schoar, 2020).

Existing studies have not examined the economic importance of mispricing versus risk compensation, nor quantified their respective contributions to cryptocurrency return variation. Our contribution fills this gap by explicitly modeling and quantifying both mispricing and risk compensation within the IPCA framework. Our results suggest that focusing solely on return comovement, whether captured by observable or latent factors, is suboptimal in the presence of structural fragmentation and market frictions.

In this respect, our work aligns with recent advances in equity markets (Kelly et al., 2019; Windmüller, 2022; Langlois, 2023), options markets (Büchner and Kelly, 2022; Goyal and Saretto, 2022), and corporate bonds (Kelly et al., 2022), which underscore the importance of distinguishing between systematic mispricing and risk compensation. Our findings suggest this distinction may be even more crucial for cryptocurrency markets given their unique structural features and the persistence of pricing inefficiencies.

# Data and Empirical Design

We collect daily data on open, high, low, and close (OHLC) prices and 24-hour trading volume from [CryptoCompare.com](https://min-api.cryptocompare.com/) and the data on on-chain activity from [IntoTheBlock.com](https://www.intotheblock.com). We screen out the so-called ``wrapped'' coins (e.g., WBTC), as they are copies of existing tokens, all stablecoins, and all synthetic derivatives (e.g., stETH, stSOL).

The main sample is from September 1st, 2017, to May 1st, 2023, where a day is defined with a start time of 00:00:00 UTC. (footnote: The sample period covers key events: the ICO mania of late 2017, the so-called ``crypto-winter'' of 2018-2019, the COVID-19 crash in March 2020, and the boom-bust cycle from 2021 to early 2022. It also covers significant institutional changes: the introduction of Bitcoin and Ether futures and Ethereum's transition from a proof-of-work to a proof-of-stake protocol.) The price and volume data are aggregated across over 80 centralized exchanges based on the exchange-specific trading volume. (footnote: The exchanges that we include in the aggregation are the ones ranked from AA to B by [CryptoCompare.com](https://min-api.cryptocompare.com/) and thus deemed to provide a sufficiently reliable trading platform. The precise ranking of all exchanges appears on the company website at [https://www.cryptocompare.com/exchanges/\#/overview](https://www.cryptocompare.com/exchanges/\#/overview).) This implies that more prominent exchanges have relatively more weight in the aggregation than more peripheral ones. In addition to volume-weighted aggregated data, we consider OHLC prices and volume from four major centralized exchanges: Binance, Bitfinex, Kraken, and Poloniex. We take the perspective of a US investor, meaning that cryptocurrencies are traded against the USD or stablecoins, such as Tether USD (USDT), USD Coin (USDC), and Binance USD (BUSD).

To ensure sample quality, we implement several data filters. First, to address survivorship bias, we include failed coins that have had at least six months of transactions. Second, we remove observations with data quality issues, such as those with a closing price of zero or negative values, as well as those with missing returns, market capitalization, or trading volume. Third, we exclude returns below $-100\%$ or above $+150\%$ on a given day to mitigate the impact of extreme outliers, which eliminates less than 0.5% of erroneous or extreme observations. Appendix A provides more details.

The final sample comprises 630 cryptocurrencies. The cross-section contains just over 70 assets in September 2017, which restricts the beginning of our sample analysis to this date due to a too small cross-section in earlier periods. We note that the size of the cross-section is primarily determined by the availability of on-chain and social media activity data, and in this respect, is comparable to existing studies, such as Cong et al. (2021). Although the cross-section is smaller than the number of existing cryptocurrencies, the market value coverage is significant, ranging from 85% at the start of the sample to 70% towards the end. Appendix A provides more details, including summary statistics for daily returns of individual cryptocurrencies in our sample.

[Insert Table 1 here]

For our empirical analysis, we construct 35 asset characteristics, following existing practice in the cryptocurrency literature (Liu et al., 2022) and adapting several measures from the mainstream asset pricing literature (Kelly et al., 2019; Freyberger et al., 2020). We group them into nine categories: core characteristics (market, size, and momentum); reversal; on-chain activity; trading activity; liquidity; speculative demand; volatility and downside risk; social media activity; and equity market exposure measures such as the equity capm beta, the equity co-skewness (Harvey and Siddique, 2000), and the equity downside beta (Ang et al., 2006). Table 1 defines characteristics briefly, while Appendix B provides more details.

## A Brief Review of Instrumented PCA

Instrumented principal component analysis (IPCA) is particularly well-suited for examining the relative importance of systematic mispricing and risk compensation, as it allows both alphas and betas to vary over time as functions of observable asset characteristics. IPCA is defined as a conditional latent factor model for returns of a cryptocurrency $i$ at time $t+1$: (footnote: We use raw returns rather than excess returns for two reasons. First, cryptocurrency markets operate continuously 24/7, whereas risk-free rate data (e.g., short-term Treasury bills) are only available during business days. This creates a fundamental data mismatch. Second, and more importantly, the risk-free rate during our sample period was economically negligible (averaged 0.01%--0.02% daily at the beginning and end of the sample, and zero during 2020--2022). This compares to average cryptocurrency returns spanning from $-7\%$ to $+12\%$ daily (see Table A2). In a set of unreported results, we document that the IPCA asset pricing performance and the factor loadings are virtually identical when using raw returns or excess returns. The results are available from the authors upon request.)
$$
\begin{aligned}
r_{i,t+1} & = \alpha_{i,t} + \beta_{i,t}f_{t+1} + \epsilon_{i,t+1},
\end{aligned}
$$
where $\mathbb{E}_t\left[\epsilon_{i,t+1}\right]=0, ~ \mathbb{E}_t\left[f_{t+1}\epsilon_{i,t+1}\right]=0$
and $f_{t+1}$ is the vector of $K$ latent factors extracted from cryptocurrency returns. Unlike standard factor models in which mispricing and factor loadings are static parameters, IPCA assumes these evolve based on asset characteristics:
$$
\begin{aligned}
\alpha_{i,t} &= \boldsymbol{z}_{i,t}^{'} \Gamma_{\alpha} + \nu_{i,t}^\alpha, \qquad \beta_{i,t} = \boldsymbol{z}_{i,t}^{'} \Gamma_{\beta}+ \nu_{i,t}^\beta,
\end{aligned}
$$
where $\Gamma = [\Gamma_{\alpha}, \Gamma_{\beta}]$ are the loadings on the $L\times1$ vector of asset characteristics $\boldsymbol{z}_{i,t}$. The scalar $\nu_{i,t}^\alpha$ and the $K\times1$ vector $\nu_{i,t}^\beta$ are orthogonal to $\boldsymbol{z}_{i,t}$, allowing for the possibility that conditional alphas and betas may not be perfectly recoverable from observable characteristics. (footnote: This specification enables returns to update quickly based on timely information contained in characteristics rather than relying on stale parameter estimates from rolling window regressions.) Critically for our analysis, this framework allows us to assess whether a given characteristic contributes to systematic mispricing (if it significantly affects $\Gamma_{\alpha}$) or risk compensation (if it significantly affects $\Gamma_{\beta}$). By comparing model specifications with ($\Gamma_{\alpha}\neq0$) and without ($\Gamma_{\alpha}=0$) the mispricing component, we can quantify the relative importance of these two explanations for cryptocurrency returns.

The model is estimated via an alternating least squares approach, which iterates the first order conditions of $f_{t+1}$ and $\Gamma=[\Gamma_{\alpha}, \Gamma_{\beta}]:$
$$
\begin{aligned}
f_{t+1}& = \left(\Gamma_\beta^{\prime}Z_t^{\prime}Z_t\Gamma_\beta\right)^{-1}\Gamma_\beta^{\prime}Z_t^{\prime}\left(r_{t+1}-Z_t\Gamma_\alpha\right)\qquad\forall t, \cr     \text{vec}\left(\Gamma\right) & = \left(\sum_{t=1}^{T-1}Z_t^{\prime}Z_t\otimes \widetilde{f}_{t+1}\widetilde{f}_{t+1}^{\prime}\right)^{-1}\left(\sum_{t=1}^{T-1}\left[Z_t\otimes\widetilde{f}_{t+1}^{\prime}\right]^{\prime}r_{t+1}\right),
\end{aligned}
$$
where $\widetilde{f}_{t+1}=\left[1, f_{t+1}^\prime\right]^\prime$, and $Z_t,\ r_{t+1}$ denote the stacked arrays of instruments and returns, respectively. To address the skewed cross-sectional distribution of some characteristics (such as market capitalisation), we cross-sectionally rank, demean, and scale $\boldsymbol{z}_{i,t}$ to be in the $\left[-0.5,\ 0.5\right]$ interval. (footnote: We follow the scaling rule of Kelly et al. (2019). For robustness, we replicate the empirical analysis by rescaling $\boldsymbol{z}_{i,t}$ to a wider $\left[-1,\ 1\right]$ interval. The results are virtually the same and are available upon request. We thank the anonymous referee for suggesting this check.)

Kelly et al. (2019) show that latent factors in IPCA can be replaced with observable portfolios while maintaining the characteristic-based conditioning:
$$
\begin{aligned}
r_{t+1} & = \boldsymbol{z}_{i,t}^{\prime}\Gamma \widetilde{g}_{t+1} + \eta_{t+1} = \text{vec}\left(\Gamma\right)^{\prime}\left(\boldsymbol{z}_{i,t}\otimes \widetilde{g}_{t+1}\right) + \eta_{i,t+1},
\end{aligned}
$$
where $\widetilde{g}_{t+1}=[1,\ g_{t+1}^\prime]^\prime$ and $g_{t+1}$ denotes the set of observable risk factors. We refer to this specification as an instrumented observable factor model and use it to verify that the importance of mispricing is robust to the choice of common factors.

# Main Empirical Results

In this section, we address our central research question regarding the importance of systematic mispricing and risk compensation in explaining cryptocurrency returns. First, we compare different IPCA specifications that allow for time-varying alphas ($\Gamma_\alpha \neq 0$) against restricted versions that force systematic mispricing to zero ($\Gamma_\alpha = 0$). Second, we investigate the economic value of systematic mispricing by computing the out-of-sample performance of portfolios formed using predicted alphas. Third, we examine the distinct sources of mispricing and risk compensation via a series of bootstrap tests.

## Asset Pricing Performance

Following Kelly et al. (2019), we compute total and predictive $R^2$ as:
$$
\begin{aligned}

R^2_{tot} &= 1 - \frac{\sum_{i,t}\left(r_{i,t+1} - \widehat{\alpha}_{i,t} -  \widehat{\beta}_{i,t}^{\prime}\widehat{f}_{t+1}\right)^2}{\sum_{i,t}r_{i,t+1}^2},\qquad R^2_{pred} = 1 - \frac{\sum_{i,t}\left(r_{i,t+1} - \widehat{\alpha}_{i,t} - \widehat{\beta}_{i,t}^{\prime}\widehat{\lambda}\right)^2}{\sum_{i,t}r_{i,t+1}^2},
\end{aligned}
$$
where $\widehat{\alpha}_{i,t}=\boldsymbol{z}_{i,t}^{'}\widehat{\Gamma}_\alpha$, $\widehat{\beta}_{i,t}=\boldsymbol{z}_{i,t}^{'}\widehat{\Gamma}_\beta$, and $\widehat{\lambda}$ is the vector of the unconditional time-series mean of the latent factors computed as $\widehat{\lambda}_k=\frac{1}{T}\sum_{t=1}^Tf_{t,k}.$ The $R_{tot}^2$ indicates the ability of a model to describe the comovements of returns and $R_{pred}^2$ the proportion of predictable variation captured by the model.

We first implement an IPCA with eight latent factors and all characteristics in Table 1 as instruments. Next, we consider an instrumented observable factor model where alphas and betas are conditioned on the same characteristics, but latent factors are replaced with observable portfolios. We employ an eleven-factor model that combines the market, size, momentum, and value factors from Liu et al. (2022), Cong et al. (2021), and Liebi (2022) with seven additional characteristic-managed portfolios, selected based on their incremental explanatory power. (footnote: The seven additional long-short portfolios are formed on characteristics that provide the highest increase in $R^2_{tot}$ within a given group: price to 90-day high price (reversal), trading volume (trading activity), maximum returns (speculative demand), Value-at-Risk (volatility and downside risk), bid-ask spread (liquidity), Facebook likes (social media activity), and equity beta (equity market exposure).) Appendix B provides descriptive statistics for the daily returns of all observable risk factors. Finally, we implement a static PCA to assess the contribution of time-varying parameters.

The comparison is based on the full sample (in-sample) and recursive (out-of-sample)
estimates. The out-of-sample performance is based on an expanding window
estimation starting from March 1st, 2020. In each period $t,$ we re-estimate the corresponding parameter $\widehat{\Gamma}_t=\left[\widehat{\Gamma}_{\alpha,t}, \widehat{\Gamma}_{\beta,t}\right]$ using all the data through $t$, i.e., expanding window, and compute the realised factor return at $t+1$ as $\widehat{f}_{t+1} = \left(\widehat{\Gamma}_{\beta,t}^{\prime}Z_t^{\prime}Z_t\widehat{\Gamma}_{\beta,t}\right)^{-1}\widehat{\Gamma}_{\beta,t}^{\prime}Z_t^{\prime}\left(r_{t+1}-Z_t\widehat{\Gamma}_{\alpha,t}\right)$. Thus, the realised IPCA factors at $t+1$ require no information beyond time $t$. To test statistically the
difference in asset pricing performance between models, we test the null hypothesis $\mathcal{H}_0: E\left[\overline{\Delta}L_j\right]=0$ where $\overline{\Delta}L_j\equiv \frac{1}{nT}\sum_{t=1}^T\sum_{i=1}^n\Delta L_{j,i,t}$ and $\Delta L_{j,i,t}=\widehat{e}_{j,i,t}^2-\widehat{e}_{bench,i,t}^2$ is the squared error loss differential between the model $j$ and a benchmark unrestricted IPCA. Appendix C details this procedure.

Table 2 presents our findings for both daily and weekly returns. (footnote: For weekly aggregation, we follow the procedure of Liu et al. (2022). Specifically, we divide each year into 52 weeks, where the first week of the year comprises the first seven days. We take the last daily observation of each characteristic in the week.) The results show how systematic mispricing and time-varying risk compensation differentially affect the model's ability to capture return comovements ($R^2_{tot}$) versus predictable return variation ($R^2_{pred}$).

[Insert Table 2 here]

Allowing for systematic mispricing ($\Gamma_\alpha \neq 0$) primarily enhances return predictability without affecting comovement patterns. Restricting mispricing to zero ($\Gamma_\alpha = 0$) leaves the total $R^2$ virtually unchanged (-0.43% for IPCA) but dramatically reduces predictive $R^2$ by 18.11% in-sample and 15.06% out-of-sample for daily returns. This pattern indicates that systematic mispricing represents a substantial source of predictable return variation that operates independently of the underlying factor structure. The importance of systematic mispricing extends beyond latent factors. For instrumented observable factors, eliminating mispricing reduces predictive $R^2$ by 68.99% (0.26% versus 0.08%) and 58.52% (1.62% versus 0.67%) for daily and weekly returns.

Time-varying risk compensation involves a fundamental trade-off between capturing comovements and generating predictable returns. The comparison between IPCA and static PCA reveals this tension clearly. Static PCA achieves a higher total $R^2$ (an increase of 11.03% for daily returns), indicating a superior ability to capture pure return comovements. However, PCA dramatically underperforms in terms of the predictive $R^2$ as we observe a reduction of 62.20% (0.26% versus 0.10%) in predictive metrics. Furthermore, static PCA generates negative out-of-sample $R^2$ statistics.

The complementary nature of these components explains IPCA's superior performance. Using latent factors enhances the model's ability to capture return comovements compared to pre-specified portfolios, i.e., higher total $R^2$. Simultaneously, instrumenting alphas on characteristics substantially improves the model's ability to generate predictable return variation, i.e., higher predictive $R^2$.

## Economic Evaluation of Mispricing

We now investigate whether investors can profit from detecting systematic mispricing, as captured by the IPCA. To this end, we form a ``pure-alpha'' portfolio based on IPCA's estimate of $\widehat{\Gamma}_{\alpha}$. At the end of the day (week) $t-1$, we estimate the model using the historical data and obtain parameter estimates $\widehat{\Gamma}_{\alpha,t-1}$. We construct the portfolio with weights $w_{t-1} = \boldsymbol{z}_{t-1} \left(\boldsymbol{z}_{t-1}^{'}\boldsymbol{z}_{t-1}\right)^{-1} \widehat{\Gamma}_{t-1}$, which combines the individial assets in proportion to their expected returns beyond the exposure to the latent factors. The portfolio construction starts in March 2020, which corresponds to the beginning of the out-of-sample period.

Table 3 reports the daily and weekly results. The pure-alpha portfolios generate highly significant risk-adjusted returns, with t-statistics consistently exceeding 7 (10) for daily (weekly) estimation across specifications. The Sharpe ratios exceed 0.7 per week in most cases. Most interestingly, the performance of the portfolios remains stable as we increase the number of latent factors to eight, which is consistent with significant systematic mispricing irrespective of return commonality. The robustness of these results across different risk adjustment models—from simple CAPM to the extended eleven-factor specification—demonstrates that additional risk factors cannot explain away the economic value of systematic mispricing. This further supports the assumption that systematic mispricing represents a persistent and economically relevant feature in cryptocurrency markets rather than a statistical artifact.

[Insert Table 3 here]

## Which Characteristics Matter for Alphas and Betas?

We now investigate which groups of characteristics drive systematic mispricing and risk compensation. In our analysis, we identify the distinct sources of two components of cryptocurrency returns and quantify their significance over time. We implement bootstrap simulations to test the significance of groups of characteristics for conditional alphas ($\alpha_{i,t}$) and betas ($\beta_{i,t}$). For systematic mispricing, we test $\mathcal{H}_0: \Gamma_\alpha^g = 0$, where $\Gamma_\alpha^g$ is the subvector corresponding to a particular characteristic group. We compute a Wald-type test statistic $W_\alpha^g=\widehat{\Gamma}_\alpha^{g \prime}\widehat{\Gamma}_\alpha^g$ and obtain p-values using wild bootstrap simulations following Kelly et al. (2019). (footnote: The null hypothesis $\mathcal{H}_0: \Gamma_\alpha^g = 0$ does not rule out temporary mispricing, as long as mispricing is truly idiosyncratic and unassociated with asset characteristics.) For risk compensation, we implement analogous tests for factor loadings ($\Gamma_\beta^g = 0$).

**Systematic mispricing drivers.** Table 4 reveals distinct patterns for daily (Panel A) and weekly (Panel B) returns. For daily returns, two groups of characteristics are important for systematic mispricing: speculative demand maintains strong significance across models (p-values below 0.05), and liquidity shows robust significance throughout. All other characteristic groups lose significance as more factors are included. For weekly returns, reversal characteristics become highly significant across all specifications, although speculative demand and liquidity remain important. This suggests that mispricing operates through behavioral channels (speculative demand) and microstructure frictions (liquidity and reversal).

[Insert Table 4 here]

To examine the time-varying nature of systematic mispricing, we estimate the eight-factor IPCA using a two-year rolling window and implement bootstrap tests for each period. Figure 1 shows test statistics along with bootstrap percentiles for daily returns. Mispricing is a persistent phenomenon throughout our sample. Speculative demand exhibits the strongest and most consistent significance, intensifying during the 2021 cryptocurrency boom and remaining elevated through 2022. Liquidity effects are pronounced during the early period and the COVID-19 pandemic, when trading frictions were most severe.

[Insert Figure 1 here]

Weekly results (Figure 2) show the persistent statistical significance of conditional alphas over time. Consistent with unconditional bootstrap tests, reversal characteristics drive systematic mispricing throughout the whole sample, whereas volatility characteristics gain prominence during the 2021-2022 market cycle. Appendix D reports the significance of other groups for daily (Figure A1) and weekly (Figure A2) returns. These results show that other characteristics do not influence mispricing over time.

[Insert Figure 2 here]

We note that the evidence of significant mispricing in cryptocurrency returns, reflecting behavioral biases (speculative demand) and microstructural frictions (liquidity risk), presents an interesting comparison with findings from equity markets, which show that demand for lottery-like assets leads to overpricing of illiquid assets (Kumar, 2009; Bali et al., 2011).

**Risk compensation drivers.** Table 5 shows that the determinants of conditional betas differ substantially from those of alphas. Core characteristics (market, size, and momentum) are consistently significant across factor specifications. For daily returns, equity market exposure becomes strongly significant in larger factor models (p-value = 0.00 with $K=7,8$), while speculative demand and volatility characteristics also gain significance. For weekly returns, core characteristics maintain strong significance, alongside reversal and trading activity.

[Insert Table 5 here]

Figure 3 shows how different characteristics affect factor loadings over time. Core characteristics and equity market exposure consistently demonstrate importance, particularly after 2020, suggesting a growing integration between cryptocurrency and equity markets. Volatility and downside risk also represent a key feature for risk compensation, whereas speculative demand shows relevance at the beginning and towards the end of the sample.

[Insert Figure 3 here]

Figure 4 reports the bootstrap statistics for weekly betas over time. The main insights align with the daily results. Core characteristics have a significant influence on risk compensation, with exposure to the equity market also representing a considerable feature that drives conditional betas. Unlike daily results, volatility and downside risks are less relevant, whereas reversal and trading activity gain significant prominence in the dynamics of factor loadings. (footnote: As detailed in the appendix, the significance for other characteristic groups confirms the patterns observed in the unconditional tests - most groups do not systematically drive risk compensation over time.)

[Insert Figure 4 here]

The results overall suggest that while mispricing persists through behavioral and structural channels that resist arbitrage, risk compensation increasingly follows established asset pricing mechanisms. Furthermore, exposure to equity markets suggests that cryptocurrency systematic risk reflects broader market factors rather than solely crypto-specific risks.

We complement our analysis by performing two additional exercises. First, we further test the relevance of individual characteristics instead of groups for betas. This provides a more granular picture of which characteristics are most important within groups. We show that a few characteristics drive the significance of the most important groups. Regarding the strong role of equity characteristics in driving factor loadings, exposure to equity market returns (including their downside movements) matters for the risk compensation of cryptocurrencies.

Second, we augment the bootstrap significance tests by measuring the relative contribution of different groups of characteristics to the sum of squared alpha and beta parameters. We delegate the details of this exercise to the appendix and discuss the main results here. Focusing on contributions to daily alphas, speculative demand tends to account for the large share throughout the sample, with its impact increasing from mid-2020 to the end of 2022, consistent with the strong statistical significance reported in Figure 1. Similarly, the economic impact of liquidity characteristics is more substantial during the early sample period, consistent with their statistical importance. We observe a similar degree of association between the statistical and economic relevance of variables for weekly alphas. Turning to betas, we find that the relative contributions of various groups exhibit similar patterns for daily and weekly factor loadings. Furthermore, the economic impact of groups of characteristics on daily and weekly betas is also associated with their statistical significance.

## Asset Quality and Model Performance

To gain additional insight into the impact of modelling mispricing and risk compensation on asset pricing performance, we compute the $R^2$ statistics for coins grouped by different characteristics. Each day, we sort the cryptocurrencies into quartiles based on various variables, one at a time. For each quartile, we compute the total and predictive $R^2$ for the eight-factor IPCA, eight-factor PCA, and a dynamic observable eleven-factor model instrumented by all characteristics. We compare these different approaches to better understand where various modelling mechanisms (time-varying coefficients and latent factors) are most relevant. Following Kelly et al. (2019), we do not re-estimate models for different subsamples, as this would mechanically improve fit. Instead, we keep factors and parameters fixed at their full-sample estimates and recalculate $R^2$ statistics within each subsample.

Table 6 shows daily results for quartiles with the lowest and highest values of a given characteristic. Focusing on the total $R^2$, IPCA maintains substantial advantages over instrumented observable factors for volatile and illiquid assets, with IPCA outperforming by 62-63% for high volatility cryptocurrencies. For larger, more liquid assets, instrumented observable factors often align with IPCA performance. Static PCA shows mixed performance relative to IPCA. For lower-quality assets, it typically underperforms IPCA in $R^2_{pred}$ by 75-90%, but often outperforms in $R^2_{tot}$ by 10-20%. This suggests that while static PCA can capture realized return variation, it struggles with prediction for assets where mispricing effects are most pronounced.

[Insert Table 6 here]

Turning to the predictive $R^2,$ IPCA demonstrates its strongest relative performance among lower-quality assets. For instance, IPCA achieves an $R^2_{pred}$ of 0.42% among cryptocurrencies with the highest idiosyncratic volatility compared to 0.10% for observable factors, representing a 76% underperformance by the conditional observable factor model that ignores mispricing. Similar patterns emerge for illiquid assets with the highest bid-ask spreads, where IPCA generates 0.58% $R^2_{pred}$ versus 0.12% for observable factors (a 79% underperformance). The pattern extends to speculative demand ({\tt max}), where observable factors achieve only 0.09% compared to IPCA's 0.40%. In contrast, IPCA's $R^2_{pred}$ is negative or near-zero for large, more liquid, less volatile assets with more social media and on-chain activity.

These results suggest that the impact of mispricing on the $R^2_{pred}$ is not straightforward. The time-varying alphas make a positive contribution to the predictive performance for smaller and illiquid cryptocurrencies. This likely happens because the mispricing of these cryptocurrencies is more significant and time-varying. However, frequent changes in alphas are detrimental to the return prediction of larger and liquid cryptocurrencies, as their mispricing is likely less significant. Since the cross-section tends to be skewed towards smaller and illiquid cryptocurrencies, the IPCA produces, on average, the higher $R^2_{pred}$ statistics when allowing for systematic mispricing.

Overall, Table 6 provides strong empirical validation that the advantages from time-varying alphas are systematically concentrated where economic theory predicts mispricing should be most prevalent---among assets with high arbitrage costs and limited liquidity. The weekly frequency---as shown in Table A5 in in the appendix---amplifies the distinction between asset quality segments, suggesting that the benefits of modeling systematic mispricing and time-varying exposures are particularly pronounced over coarser frequencies, especially for assets where arbitrage constraints are most binding.

## Additional Checks

**Volatility-scaled returns.** We examine the impact of extreme volatility on the role of time-varying mispricing and risk compensation on cryptocurrency returns. To this end, we scale individual returns by their previous month's realised volatility. This transformation reduces cross-sectional heteroskedasticity. While keeping the characteristics unchanged, we re-estimate IPCA, PCA, and observable factors using scaled returns. We delegate the details of this exercise to the appendix and discuss the main results here.

Regarding the total $R^2$, volatility scaling diminishes the gap between observable and latent factor models, although it remains statistically significant. More importantly, Table A6 in the appendix confirms that the role of mispricing remains crucial irrespective of return scaling. For IPCA, restricting alphas to zero ($\Gamma_\alpha = 0$) significantly reduces predictive $R^2$ by 5.44% for daily returns. Similarly, for instrumented observable factors, constraining alphas reduces predictive metrics by 67.24%, and for PCA by 67.34%. The results for weekly returns show similar patterns. This provides evidence that the role of systematic mispricing in explaining cryptocurrency returns is not merely an artifact of extreme differences in volatility.

**Data sampled from individual exchanges.** The main empirical results are based on a volume-weighted aggregation of prices and volume across different exchanges. To mitigate concerns that the aggregation might critically affect the IPCA performance, we now replicate the main analysis for daily returns of cryptocurrencies from major exchanges: Kraken, Coinbase, Binance, and Bitfinex. These rank among the largest exchanges in terms of trading volume.

The results, reported in the appendix, show that IPCA's outperformance becomes even more pronounced, with performance gaps of 30--59% relative to observable factors compared to smaller gaps in aggregated data. The results also reveal substantial heterogeneity across exchanges, with some venues exhibiting much stronger evidence of systematic mispricing. Comparing the unrestricted IPCA with the constrained version ($\Gamma_\alpha = 0$) reveals that modeling systematic mispricing is particularly critical on certain exchanges. For instance, Bitfinex shows a 63% decline in predictive $R^2$ when alphas are constrained to zero, while Kraken shows a 7% decline. This suggests that volume-weighted aggregation may actually understate the extent of mispricing. In this respect, our main results likely represent a lower bound for the importance of mispricing to explain the predictable variation in cryptocurrency returns.

It is important to note that, since we focus on data from individual exchanges, the cross-sectional and time-series dimensions differ for each separate estimation compared to the aggregate sample. As a result, the heterogeneity in the results might be due to sample differences. Yet, the results provide widespread evidence in favour of allowing for systematic mispricing in the IPCA specification, especially for predictive $R^2$.

**Replacing observable factors with managed portfolios.** Guided by the previous insights, we investigate the asset pricing performance of IPCA when observable risk factors are replaced by characteristic-managed portfolios. The latter are constructed based on the 35 asset characteristics described in Table 1 as $x_{t+1}=\frac{Z_t^\prime r_{t+1}}{N_{t+1}}$, where $N_{t+1}$ is the number of non-missing observations at time $t+1$, $r_{t+1}$ is the $N_{t+1}\times 1$ vector of individual asset returns, and $Z_t$ is the $N_{t+1}\times L$ matrix that stacks individual characteristics. (footnote: In this respect, each element of $x_{t+1}$ represents a weighted average of cryptocurrency returns with weights determined by the value of characteristics at a given time.)

We select a parsimonious set of managed portfolios that jointly approximate latent factors by regressing each IPCA factor on the value-weighted cryptocurrency market and all managed portfolios. Given the large number of characteristics, we perform regularisation via elastic-net (Zou and Hastie, 2005) and allow at most two non-zero coefficients in each regression. This selection procedure identifies eleven characteristic-managed portfolios formed on {\tt capm $\beta$}, {\tt r21_1}, {\tt bm}, {\tt to}, {\tt bidask}, {\tt max $30$}, {\tt rvol}, {\tt down $\beta$}, {\tt equity capm $\beta$}, {\tt equity down $\beta$}, and the value-weighted cryptocurrency market. These eleven portfolios jointly explain from 60% to 80% of the variation in IPCA factors.

Table A4 in the appendix shows that IPCA retains the highest explanatory power, followed by the instrumented managed portfolios, with instrumented observable factors performing worse. Managed portfolios achieve an $R^2_{tot}$ of 13.99%, compared to 10.56% for observable factors --- a statistically significant 32% performance gap.

More importantly, the role of mispricing is retained when observable risk factors are replaced with characteristic-managed portfolios. When mispricing is unrestricted ($\Gamma_\alpha \neq 0$), the out-of-sample predictive $R^2$ from instrumented managed portfolios increases from 0.05% to 0.25%, almost a fivefold increase. These results demonstrate that allowing for unconstrained mispricing increases predictive ability regardless of whether factors are latent or approximated using characteristics.

# Interpreting the IPCA Factors

The factors extracted from IPCA are ordered by their variance and are only identifiable up to a rotation. By construction, each factor may be influenced by all characteristics. Since characteristics are likely correlated, the orthogonality condition on latent factors implies that none of them will exactly match a single characteristic. Thus, any labelling is imperfect. Nevertheless, we attempt to provide an economic interpretation of latent cryptocurrency factors in the eight-factor IPCA estimated on the full sample of daily returns.

## Latent Factors and Characteristic-Managed Portfolios

Following Ludvigson and Ng (2009), we first examine the correlation between latent factors and managed portfolios. The left panel in Figure 5 shows the marginal $R^2$, which is the $R^2$ statistic from univariate regressions of each characteristic-managed portfolio on each latent factor. (footnote: Notice the individual $R^2$ for each factor can be cumulated as they are orthogonal to each other.) The first latent factor (F1) is primarily associated with volatility measures, showing the highest correlations with `rvol`, `rskew`, and `std_vol`. The second factor (F2) captures the exposure to the equity market and liquidity risk, with the strongest correlations observed for `equity capm $\beta$`, `to` (turnover), and `illiq`.

[Insert Figure 5 here]

The third factor (F3) correlates most strongly with `down $\beta$` and `capm $\beta$`. This echoes the sixth factor, which shows the highest correlations with `down $\beta$`, `capm $\beta$`, in addition to `std_vol`. The fourth factor (F4) emerges as the primary momentum factor, showing strong explanatory power for `r30_1`, `r21_1`, and `r7_1`. The fifth factor (F5) exhibits a distinctive pattern, correlating most strongly with equity downside risk (`equity down $\beta$`). The seventh factor (F7) can be unambiguously identified as the value-weighted cryptocurrency market factor, accounting for 77.3% of the variation in the `vw_mkt` portfolio. Finally, the eighth factor (F8) is associated with trading frictions, exhibiting strong correlations with `bidask`, `rvol`, and speculative demand measures such as `max 30`.

The right panel of Figure 5 shows the results of a complementary regression analysis. We implement a multivariate regression in which all standardized latent factors are projected onto each standardized managed portfolio. Since the regression does not include an intercept, each coefficient can be interpreted as a partial correlation coefficient. The darker the colour in the heatmap, the larger the partial correlation.

The results largely confirm the evidence from the left panel in Figure 5. Factor 1 (F1) exhibits strong positive correlations with volatility measures, and Factor 2 (F2) shows strong correlations with trading activity, in addition to a strong correlation with the equity market `equity capm $\beta$`. Factor 3 (F3) displays a strong positive correlation with `down $\beta$` but a negative correlation with `capm $\beta$`. Factor 4 (F4) confirms its role as the momentum factor, whereas Factor 5 (F5) shows an interesting dual pattern, with a strong negative correlation with `equity down $\beta$` but positive correlations with momentum measures. Factors 6 (F6) and 7 (F7) exhibit strong correlations with broad market risk measures. In particular, the return on F7 is highly related to the return on the market portfolio `vw_mkt`. Finally, Factor 8 (F8) demonstrates strong positive correlations with liquidity frictions and extreme returns.

## Correlation With Equity Risk Factors

In this section, we address a fundamental question that has been central to the debate among market participants and researchers: do cryptocurrencies and traditional asset classes share common risk factors? The factor structure we have identified via IPCA suggests potential linkages with equity markets that warrant investigation. Notably, the fifth IPCA factor (F5) shows a distinctive pattern with equity-related characteristics, exhibiting the strongest correlation with `equity down $\beta$` in the marginal $R^2$ analysis and a strong negative partial correlation in the multivariate regression analysis. Similarly, the second factor (F2) demonstrates significant correlations with `equity capm $\beta$`, suggesting potential cross-market risk transmission.

**IPCA bootstrap tests** To investigate these linkages more formally, we start by leveraging the flexibility of IPCA and consider an extended model that includes both latent cryptocurrency factors and observable equity factors:
$$
r_{i,t+1} = \alpha_{i,t}^{\prime} + \beta_{i,t}^{\prime}f_{t+1} + \delta_{i,t}^{\prime}g_{t+1} + \epsilon_{i,t+1},
$$
in which $\alpha_{i,t}^{\prime}, \beta_{i,t}^{\prime},$ and $\delta_{i,t}^{\prime}$ are time-varying coefficients instrumented with all characteristics. Here, $f_{t+1}$ and $g_{t+1}$ represent the latent cryptocurrency factors and the observable equity factors, respectively. The incremental explanatory power of equity factors can be tested using a Wald-like statistic for the null hypothesis $\mathcal{H}_0: \Gamma_\delta=\boldsymbol{0}_{L\times M}$ (see Appendix D for details). (footnote: The incremental explanatory power of equity factors can be tested using a Wald-like statistic $W_\delta =\text{vec}\left(\widehat{\Gamma}_\delta\right)^{\prime}\text{vec}\left(\widehat{\Gamma}_\delta\right)$ for the null hypothesis $\mathcal{H}_0: \Gamma_\delta=\boldsymbol{0}_{L\times M}.$ $W_\delta$ measures the distance between the model with and without $g_{t+1}.$ If it is large relative to bootstrap values, $g_{t+1}$ contributes significantly to explaining the cryptocurrency returns.). We consider the five equity factors of Fama and French (2015) -- the market (MKT), size (SMB), value (HML), profitability (RMW), and investment (CMA) -- and momentum (MOM) of Jegadeesh and Titman (1993). (footnote: Notice that, unlike equity markets, cryptocurrency markets operate on a 24/7 basis. Thus, we merge the datasets by retaining only those dates for which we have available observations for both.)

Table 7 reports the p-values on testing the significance of $\delta_{i,t}^{\prime}$. The results on individual tests, which examine the individual significance of each equity factor separately, provide mixed evidence. The p-values for HML decline systematically from 0.60 in the single-factor model to 0.02 in the eight-factor specification. This finding aligns with recent evidence that value-like characteristics matter for cryptocurrency pricing (Cong et al., 2021; Liebi, 2022). The market factor (MKT) shows moderate evidence of correlation, with p-values improving from 0.79 to 0.50 as the number of latent factors increases, though this falls short of conventional significance levels. The momentum factor (MOM) displays marginal significance in higher-factor specifications, particularly in IPCA6 (p-value = 0.11) and IPCA7 (p-value = 0.07). In contrast, the size (SMB), profitability (RMW), and investment (CMA) factors show no significance across all specifications.

[Insert Table 7 here]

When including all equity factors simultaneously, the results reveal more substantial evidence for certain factors. Most notably, MOM achieves statistical significance in several specifications, with p-values of 0.05 in IPCA5, 0.01 in IPCA7, and 0.06 in IPCA8. The value factor (HML) maintains its significance in joint tests, particularly in IPCA6 and IPCA8, where p-values reach 0.03 and 0.06, respectively.

**Factor-spanning regressions** In addition to the IPCA-based bootstrap tests, we conduct factor-spanning regressions that directly test whether IPCA factors can be replicated using linear combinations of equity risk factors. Table 8 reports the results where each IPCA latent factor is regressed on the six equity risk factors. Five out of eight IPCA factors exhibit negative adjusted $R^2$ values, indicating that most equity factors provide no meaningful explanatory power. However, a notable exception is the seventh factor (F7), which exhibits a substantial correlation with equity risk factors, achieving an adjusted $R^2$ of 9.1%. This finding is consistent with our earlier interpretation of F7 (see Figure 5), which showed the strongest correlation with the value-weighted cryptocurrency market portfolio ($R^2 = 77.3\%$).

[Insert Table 8 here]

The regression intercepts provide additional evidence on the correlation between equity and cryptocurrency market returns. If equity risk factors could fully explain IPCA factors, the intercepts should be statistically indistinguishable from zero. This is indeed the case for the seventh IPCA latent factor (F7). The statistically insignificant intercept suggests that the equity market returns fully capture the presence of systematic components in the seventh IPCA cryptocurrency factor.

To provide additional insight into the temporal evolution of cryptocurrency-equity correlations, Figure 6 presents  2-year rolling-window estimates of the significance of market (MKT) and value (HML) factors for the two IPCA factors that showed the strongest correlations in our spanning regression analysis. The results provide important context for interpreting the static regression results in Table 8.

[Insert Figure 6 here]

The rolling window analysis reveals a dramatic structural shift around March 2020. Panel A shows that F6 and F7 exhibited virtually no significant correlation with the equity market during 2018 to early 2020, with p-values consistently above 0.6. However, from March 2020 onward, both factors exhibit much stronger and more persistent correlations with equity markets, with p-values frequently dropping below the 5% significance threshold. F7 shows particularly strong significance during 2020-2021, with p-values near zero. Panel B shows intermittent but significant correlations between the value factor and IPCA factors, with distinct periods of high significance during 2019-2020 and 2021-2022.

The sharp increase in correlations after March 2020 aligns with accelerated institutional adoption and the integration of cryptocurrencies into traditional investment portfolios during the pandemic (Didisheim and Somoza, 2022). Increasingly correlated trading could lead to cross-asset class correlations, even if the two markets are not fully integrated (Kyle, 1989). This evolution supports the theoretical framework of Pástor and Veronesi (2009), where increased investor exposure to innovative sectors reduces information asymmetries and strengthens risk spillovers between asset classes.

The convergence of evidence from our empirical approaches reveals a nuanced picture of cryptocurrency-equity factor relationships. While the bootstrap tests show mixed significance patterns, the spanning regressions provide more convincing evidence in favour of strong time-varying correlations between cryptocurrency and equity markets. These seemingly contradictory results are reconciled by recognizing that the modest correlations documented in our static tests mask substantial temporal variation in the underlying relationships.

# Conclusion

Our analysis reveals that cryptocurrency returns reflect both systematic mispricing and risk compensation, each operating through distinct economic mechanisms. The persistence of behavioral-driven mispricing alongside increasingly traditional risk-return relationships suggests that cryptocurrency markets occupy a unique position—more efficient than pure speculation, yet less efficient than mature asset classes.

The growing correlation between cryptocurrency and equity factors indicates market evolution toward greater integration with traditional finance. This has important implications as institutional adoption continues: while systematic risk compensation may converge toward equity market patterns, the structural features that enable persistent mispricing—such as fragmentation, high arbitrage costs, and heterogeneous investor bases—are likely to remain.

An interesting venue for future research could be to examine how regulatory developments and institutional infrastructure affect the balance between mispricing and risk compensation, and whether the patterns we document extend to other emerging asset classes characterized by high speculation and limited arbitrage capital.

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%Bibliography

\begin{spacing}{2}
\bibliographystyle{JFQA}


---

# Internet Appendix

## Data Cleaning

This section provides a full description of the procedure used to source, clean, and prepare the main database. The replication package will be available on the publisher's website.

### Original Sources

\begin{enumerate}
\item We utilize [CryptoCompare](https://min-api.cryptocompare.com/) to obtain daily aggregated and exchange-level OHLC pricing and volume data, where a day is defined as starting at 00:00:00 UTC. We set tryConversion to `true' and the tsym parameter to `USD', `USDT', `USDC', or 'BUSD' for the aggregated data in the main empirical analysis. This means that if the cryptocurrency does not trade directly into the requested symbol, BTC (or another available trading pair) will be used for conversion.

\item Daily blockchain and social media activity, such as the number of new addresses and the number of active Reddit accounts, are sourced via [IntoTheBlock.com](https://www.intotheblock.com) and downloaded based on [CryptoCompare](https://min-api.cryptocompare.com/). Again, a day is defined as starting at 00:00:00 UTC.
\end{enumerate}

### Data Pre-Processing

We retain only those cryptocurrencies for which we do have at least some available data on on-chain and social media activity. (footnote: This means that only tickers returned by CryptoCompare’s blockchain list endpoint `/data/blockchain/list` are considered.) We implement a variety of pre-processing steps to ensure a cryptocurrency is included in the final sample, aiming to minimize the impact of measurement errors and price staleness, such as:
\begin{itemize}
\item[$-$] Drop observations with zero or missing values for the close price.
\item[$-$] Drop observations with $`NaN`$ returns, market capitalization, or volume.
\item[$-$] Exclude outlying returns below -100% and above 150%.
\item[$-$]{\tt Cryptocurrency type.} We utilize cryptocurrency classification data from [CoinMarketCap](https://coinmarketcap.com/cryptocurrency-category/) and screen out all cryptocurrencies which:

\begin{itemize}
\item[$-$] are linked, backed by, or track the price of gold or any precious metal,
\item[$-$] are so-called ``wrapped'' coins (e.g., WBTC),
\item[$-$] are stablecoins, including those that are centralized (e.g., USDT, USDC) or algorithmically stabilized (e.g., DAI, UST),
\item[$-$] are centralized exchange-based coins that are derivatives  (e.g., stETH, stSOL).
\end{itemize}
\end{itemize}

We note that [CryptoCompare.com](https://min-api.cryptocompare.com/) implements a series of filters to address API issues and suspicious trading activity. These can be summarized as follows:
\begin{itemize}
\item Trade outliers are automatically excluded from the calculation of trading volume and therefore from the volume-weighting scheme. For a trade to be considered an outlier, it must deviate significantly from either the median of the set of exchanges or the previous aggregate price. (footnote: Such deviations can occur for a number of reasons, such as extremely low liquidity on a particular cryptocurrency, erroneous data from an exchange, or the incorrect mapping of a cryptocurrency in the API.)

\item Constituent exchanges for the value-weighted aggregation are reviewed regularly and excluded if (1) posted prices are too volatile compared to the market average of a given cryptocurrency, (2) trading has been suspended by the exchange on a given day, (3) verified user or social media reports false data provision, or (4) malfunctioning of their public API.
\end{itemize}

[Insert Table A1 here]

These steps mitigate the effect of fake volume and substantially reduce the empirical analysis's exposure to concerns about misreporting of trading activity for some exchanges. (footnote: Two additional comments are in order. First, notice that ``fake'' trading typically takes place on crypto-to-crypto trading on single, possibly small, exchanges that inflate trading volume in order to attract Initial Coin Offering (ICO) listings or to manipulate the market (see, e.g., (Li et al., 2018)). By considering trading against a fiat currency and aggregating data from a large cross-section of exchanges, the risk that manipulation on a single exchange could affect overall market activity is substantially mitigated. Second, the fact that we focus on transactions on regular trading exchanges should mitigate the concern that market activity is primarily driven by illegal activities. The latter typically do not take place on registered centralized exchanges but through peer-to-peer transactions on the blockchain (see, e.g., (Foley et al., 2019), (Griffin and Shams, 2020)).)

### Daily Returns of Individual Cryptocurrencies

Table A1 reports summary statistics of our dataset after applying all filters. The sample includes 630 cryptocurrencies with the cross-section changing over time. The market capitalization covered by these coins also fluctuates and tends to account for above 70% of the total market capitalization of all available cryptocurrencies. Table A2 shows descriptive statistics for daily returns of cryptocurrencies in the final sample. Although reported statistics exhibit extreme outliers, as demonstrated by the minimum and maximum values in the first and last rows, the vast majority of cryptocurrencies in our sample have relatively moderate values. Slightly more than half of the assets earn negative average returns and Sharpe ratios, whereas the majority of cryptocurrencies exhibit a positive skewness. The maximum (minimum) daily returns are never above (below) 150% (-100%) due to our filtering criteria.

[Insert Table A2 here]

## Cryptocurrency Characteristics and Observable Factors

### Cryptocurrency Characteristics

We create a list of 35 asset characteristics and divide them into nine categories: core characteristics (market, size, and momentum); reversal; on-chain activity; trading activity; liquidity; speculative demand; volatility and downside risk; social media activity; and equity market exposure. These characteristics are constructed by adapting existing studies in equity markets \citep[e.g.,][]{freyberger2020dissecting} or drawing from recent work in cryptocurrency markets \citep[e.g.,][]{liu2019common,bianchi2022trading}. In the following, we expand on Table 1 in the main text to provide a more comprehensive description of each characteristic.

#### Market, size, and momentum

{\tt capm $\beta$}. 60-day rolling regression coefficient of crypto returns on the value-weighted market index, where the market return is calculated as the value-weighted average of cryptocurrency returns available in our panel on a particular day.

{\tt size}. The product of the currently available supply and the current USD price (Liu et al., 2022). The current supply refers to the number of coins/tokens that have been mined or generated and corresponds to the number currently in public hands, i.e., circulating in the market and/or locked/vested. This definition follows the blueprint for equity in Fama and French (1993).

{\tt r$l$_1}. The cumulative return from $l = 14, 21, 30$ days to one day before the return prediction (Liu et al., 2022).

#### Reversal

{\tt r2_1}. The daily return before the day of the return prediction. This is an adaptation of Jegadeesh (1990) to a higher frequency setting.

{\tt r7_1}. Short-term performance is calculated as the cumulative return from seven days to one day before the return prediction.

{\tt r180_60}. Long-term reversal is calculated as the cumulative return from 180 to 60 days before the return prediction. This is an adaptation of De Bondt and Thaler (1985) to a higher frequency setting.

{\tt rel_to_high}. The previous day's price divided by the 90-day maximum price. This adapts the logic in George and Hwang (2004) to a shorter time span.

#### On-chain activity

{\tt new add}. The number of unique addresses that appeared for the first time in a transaction of the native coin in the network (Liu et al., 2021).

{\tt active add}. The number of unique addresses active in the network, either as a sender or receiver. Only addresses that are active in successful transactions are included in the count. This approximates the network growth and the adoption base (Pagnotta and Buraschi, 2018).

{\tt bm}. The ratio of the cumulative number of unique addresses to the market capitalization. The number of unique addresses is used as a proxy for the fundamental value (Pagnotta and Buraschi, 2018). The ``network-to-market ratio'' represents a crude approximation of a valuation ratio similar to book-to-market in equity markets (Cong et al., 2021; Liebi, 2022).

#### Trading activity

{\tt $vol}. Total dollar amount of a cryptocurrency traded on a given day.

{\tt turnover}. Last day's trading volume in $ over the current market capitalization (Datar et al., 1998).

{\tt std_vol}. The standard deviation of daily log-trading volume occurred in the previous 30 days (Chordia et al., 2001).

{\tt cv_vol}. The 30-day rolling standard deviation over the 30-day rolling mean of daily trading volume (Babiak and Erdis, 2022).

#### Liquidity

{\tt illiq}. The 30-day rolling average of daily ratios between the absolute daily return and daily dollar trading volume, times a scaling constant (Amihud, 2002).

{\tt bid-ask}. The bid-ask spread is the average of two synthetic approximations based on OHLC prices by Abdi and Ranaldo (2017) and Corwin and Schultz (2012). We calculate both proxies and take the average between the two for each day and cryptocurrency pair.

{\tt vol shock 30d}. Standardized deviations from the 30-day rolling mean of log volume (Llorente et al., 2002; Babiak et al., 2022).

{\tt dto}. Individual turnover minus the daily market turnover, detrended by 180-day rolling median (Garfinkel, 2009). The daily market turnover is a value-weighted aggregation of the individual assets' turnover.

#### Speculative demand

{\tt max 30}. Maximum daily return in the previous 30 days (Bali et al., 2011; Babiak and Bianchi, 2025).

{\tt max 30(4)}. Average of the four highest daily returns in the previous 30 days (Bali et al., 2011; Babiak and Bianchi, 2025).

{\tt rskew}. The realised skewness of daily returns in the previous 30 days.

{\tt co-skew}. The sensitivity to market skewness risk is calculated as in Harvey and Siddique (2000). The calculation is implemented based on a rolling window of 30 days.

#### Volatility and downside risk

{\tt rvol}. Daily RiskMetrics volatility estimate, calculated as the exponential weighted moving average of the squared returns with weight $\lambda=0.94$.

{\tt ivol}. The standard deviation of residuals from a 60-day rolling regression of crypto returns on the value-weighted market index.

{\tt VaR(5%)}. The historical Value-at-Risk at 5% calculated based on the past 90-day returns.

{\tt down $\beta$}. 60-day rolling regression coefficient of crypto returns on the value-weighted market index, conditional on the market return being negative (Ang et al., 2006).

#### Social media activity

{\tt fb_likes}. The daily number of cumulative Facebook likes.

{\tt reddit_act}. The number of active subscribers in a day on the official Reddit channel of a given cryptocurrency.

{\tt reddit_posts}. The daily number of Reddit posts on the official Reddit channel of a given cryptocurrency.

{\tt twitter_f}. The daily number of followers for the official Twitter page of a given cryptocurrency.

#### Equity market exposure

Given the traditional view of market segmentation between cryptocurrency and equity markets, we include three characteristics to capture potential spillover effects and cross-market dependencies that may have evolved over time.

{\tt equity capm $\beta$}. 60-day rolling window regression of cryptocurrency returns on the excess returns on the equity market portfolio as in Fama and French (1993).

{\tt equity co-skewness}. Co-skewness between the cryptocurrency return and the returns on the equity market portfolio. Calculation is implemented as in Harvey and Siddique (2000).

{\tt equity downside $\beta$}. 60-day rolling regression coefficient of crypto returns on the equity market index returns, conditional on the equity market return being negative (Ang et al., 2006).

### Observable Factors

We construct the value-weighted cryptocurrency market portfolio and additional observable factors for asset characteristics described above. Following the standard approach in asset pricing literature (Fama and French, 1993), we form long-short portfolios by sorting cryptocurrencies into quintiles based on each characteristic and taking the return spread between the top and bottom quintiles. These portfolios serve as observable factors in our analysis and provide a benchmark for comparison with the latent factors extracted via IPCA.

Table A3 provides summary statistics for these portfolios. The results reveal several notable patterns that reflect the unique properties of cryptocurrency markets. First, the portfolio returns exhibit substantial volatility, averaging around 5% daily, which is considerably higher than typical equity factor returns. This reflects the inherent volatility of cryptocurrency markets and the pronounced differences across assets with varying characteristics.

[Insert Table A3 here]

Second, the annualized Sharpe ratios vary dramatically across characteristics, ranging from highly negative values (e.g., $-0.427$ for {\tt max 30(4)}) to moderately positive ones (e.g., $0.246$ for {\tt VaR(5%)}). The large absolute magnitudes of these ratios, while partly driven by the high average returns in some cases, also reflect the potential for substantial risk-adjusted returns in cryptocurrency markets. However, these should be interpreted cautiously, given the extreme volatility and non-normal return distributions.

Third, all portfolios exhibit significant departures from normality, as evidenced by substantial skewness and excess kurtosis. The skewness ranges from highly negative ({\tt fb_likes}: $-4.10$) to moderately positive ({\tt twitter_f}: $0.88$), while kurtosis values are universally elevated, with some exceeding 30. This indicates frequent extreme returns and fat-tailed distributions, consistent with the documented properties of cryptocurrency markets.

Some interesting pattern emerges when examining specific characteristic groups. Momentum-based characteristics ({\tt r14_1}, {\tt r21_1}, {\tt r30_1}) generally produce positive average returns with moderate Sharpe ratios, suggesting momentum effects in cryptocurrency markets. Conversely, speculative demand characteristics ({\tt max 30}, {\tt max 30(4)}) yield negative average returns, consistent with the overpricing of lottery-like assets as documented in equity markets.

## Testing Performance Differentials

We implement a direct test for equal predictive accuracy between competing asset pricing models as proposed by Qu et al. (2023). The methodology tests the null hypothesis $\mathcal{H}_0: \mathbb{E}\left[\overline{\Delta L}_j\right] = 0$, where
$$
\overline{\Delta L}_j \equiv \frac{1}{nT}\sum_{t=1}^T\sum_{i=1}^n \Delta L_{j,i,t}
$$
represents the pooled average loss differential between model $j$ and a specified benchmark model. Here, $\Delta L_{j,i,t} = \widehat{e}_{j,i,t}^2 - \widehat{e}_{\text{bench},i,t}^2$ is the squared prediction error differential between the two models for asset $i$ at time $t$. The squared prediction errors are constructed differently depending on the performance metric of interest. For the total $R^2$ comparison, we use:
$$
\widehat{e}_{j,i,t}^2 = \left(r_{i,t+1} - \widehat{\alpha}_{i,t} - \widehat{\boldsymbol{\beta}}_{i,t}' \widehat{\mathbf{f}}_{t+1}\right)^2
$$
For the predictive $R^2$ comparison, we replace $\widehat{\mathbf{f}}_{t+1}$ with $\widehat{\boldsymbol{\lambda}}$, the sample mean of factors.

Under the null hypothesis of equal predictive accuracy, the test statistic is:
$$
t_j = \frac{\sqrt{nT} \cdot \overline{\Delta L}_j}{\widehat{\sigma}(\overline{\Delta L}_j)}

$$
where $\widehat{\sigma}(\overline{\Delta L}_j)$ is a heteroskedasticity and autocorrelation consistent estimator of the standard error. Following Newey and West (1987), we account for potential serial correlation in the loss differentials. Let $R_t = n^{1/2} \sum_{i=1}^n \Delta L_{j,i,t}$ represent the cross-sectional sum of loss differentials at time $t$. We then compute:
$$
\widehat{\sigma}(\overline{\Delta L}_j) = \sqrt{\frac{1}{T} \sum_{j=-J}^J \left(1 - \frac{|j|}{J+1}\right) \widehat{\gamma}(j)}

$$
where $\widehat{\gamma}(j) = \frac{1}{T} \sum_{t=|j|+1}^T \widetilde{R}_{t-j} \widetilde{R}_t$ with $\widetilde{R}_t = R_t - \bar{R}$ and $\bar{R} = \frac{1}{T}\sum_{t=1}^T R_t$. For negative lags, we set $\widehat{\gamma}(j) = \widehat{\gamma}(-j)$.

The lag truncation parameter $J$ is chosen to balance the bias-variance trade-off in the estimation of the long-run variance. Following the recommendation in Qu et al. (2023), we set $J = 30$ for daily data and $J = 4$ for weekly data. Under standard regularity conditions and assuming $T \to \infty$, the test statistic converges in distribution to a standard normal: $t_j \overset{d}{\rightarrow} \mathcal{N}(0,1)$. We apply this test to compare the performance of IPCA against various benchmarks, including dynamic observable factor models and principal component analysis.

## Additional Empirical Results

This section presents the additional results, which are not reported in the main text.

### Bootstrap Tests

This section presents the remaining bootstrap results discussed in the main text. We report the bootstrap statistics for the groups of characteristics not presented in the main text.

**Systematic Mispricing** Figure A1 and A2 show the testing results for the significance of alphas in the IPCA model with eight factors estimated on daily and weekly returns in a rolling two-year window. The results show that none of these groups of characteristics has a statistically significant effect on the dynamics of conditional alphas over time, that is, we cannot reject the null hypothesis $\Gamma_\alpha=0$ at conventional confidence levels. Although some characteristics may become significant in specific periods (for example, core variables and social media activity during the price run-ups in 2021 and 2022), these episodes tend to be short-lived.

[Insert Figure A1 here]

[Insert Figure A2 here]

**Risk compensation** Figure A3 reports the testing results for the null hypothesis $\mathcal{H}_0: \Gamma_\beta=0$ for the groups of characteristics which are not reported in the main text. The results suggest that neither on-chain metrics nor trading and social media activities significantly drive the dynamics of conditional betas. A partial exception is reversal, which shows borderline significance between 2022 and 2023.

[Insert Figure A3 here]

Figure A4 reports the results for the weekly returns. Compared to daily results, several groups of characteristics, including on-chain activity, liquidity, and social media, tend to have a stronger impact on time-varying betas, though this influence remains insignificant at the 5% confidence level in most periods. The two groups of variables (speculative demand, volatility, and downside risk), which appear to be relevant for daily factor exposures, lose significance in the weekly analysis.

[Insert Figure A4 here]

**Beta bootstrap for individual characteristics**

We now provide additional granularity beyond the group-level analysis presented in the main text. We implement beta bootstrap significance tests for each of the 35 characteristics individually. This analysis enables us to pinpoint which characteristics underlie the group-level significance results and reveals important frequency-dependent patterns in the determinants of factor exposures. Figure A5 reports the bootstrap p-values for each characteristic. The results reveal several distinct patterns that provide economic insights into the mechanisms underlying cryptocurrency risk compensation.

[Insert Figure A5 here]

Speculative demand measures ({\tt max 30}, {\tt max 30(4)}), downside risk ({\tt down $\beta$}), and equity market exposure variables ({\tt equity capm $\beta$}, {\tt equity down $\beta$}) appear to be significant at the 5% confidence level for daily betas, but they become insignificant for weekly exposures. This suggests that lottery-like preferences and behavioral biases affect risk compensation primarily through short-term trading horizons. The significance of downside risk and equity exposure characteristics at daily frequency is consistent with sentiment contagion and noise trading being dominant forces at shorter horizons.

The persistent importance of market beta ({\tt capm $\beta$}) reinforces its role as the primary systematic risk factor in cryptocurrency markets, consistent with the CAPM's prediction that market exposure should be the dominant determinant of expected returns. More broadly, the significance of core characteristics for factor exposures seems to be primarily driven by market beta, with size and momentum variables contributing mainly at weekly frequency. The lack of significance for speculative demand characteristics in weekly factor exposures explains why this group shows weaker statistical significance in the group-level tests for weekly returns, despite its strong significance for daily returns.

### Relative Importance of Characteristics

The bootstrap tests in the main text establish the statistical significance of different groups of characteristics for conditional alphas and betas. To complement this analysis, we examine the relative economic importance of each group of characteristics by quantifying their contribution to the overall magnitude of mispricing and risk compensation. This provides economic context to the statistical significance results by measuring whether statistically significant characteristics also have a substantial economic impact.

At the end of each day or week $t$, we estimate the unrestricted eight-factor IPCA model using a two-year rolling window and save estimates $\widehat{\Gamma}_{\alpha,t-k:t}$ and $\widehat{\Gamma}_{\beta,t-k:t}$ with $k=2\cdot365$ for daily returns and $k=2\cdot53$ for weekly returns. For alpha contributions, we first compute for a group of variables the sum of squared coefficients in the corresponding subvector $\widehat{\Gamma}_{\alpha,t-k:t}^g$ and then divide by the total sum of squared coefficients in $\widehat{\Gamma}_{\alpha,t-k:t}$. Since all characteristics are scaled to lie within the interval $[-0.5, 0.5]$, their effects on alphas are directly comparable across groups. For beta contributions, we account for the difference in variances of the latent factors by weighting the squared beta parameters with the second-moment matrix of the factors. We first use the second-moment matrix of factors $S_{f,t-k:t}$ to obtain $\text{tr}(\widehat{\Gamma}_{\beta,t-k:t} S_{f,t-k:t} \widehat{\Gamma}_{\beta,t-k:t}')$. Then, we compute for a particular group of variables the weighted sum of squared coefficients in the corresponding submatrix $\widehat{\Gamma}_{\beta,t-k:t}^g$ as $\text{tr}(\widehat{\Gamma}_{\beta,t-k:t}^g S_{f,t-k:t} \widehat{\Gamma}_{\beta,t-k:t}^{g'})$ and divide by the total weighted sum of squared coefficients in $\widehat{\Gamma}_{\beta,t-k:t}$. These measures sum to one across all characteristic groups and provide a time-varying decomposition of the economic significance of different determinants of mispricing and risk compensation.

Figure A6 reports the results for daily returns (top panels) and weekly returns (bottom panels). The relative importance of characteristics for daily mispricing (top-left panel) aligns well with the recursive bootstrap tests reported in the main text. For instance, the importance of speculative demand for daily mispricing increases from 2021 to the end of 2022, whereas liquidity predominantly matters in the early part of the sample. The economic importance of volatility and downside risk measures also increases from mid-2021. At the weekly frequency (bottom-left panel), reversal characteristics become the primary driver of the mispricing dynamics, while the relevance of volatility and downside risk is more scattered throughout the sample.

[Insert Figure A6 here]

Regarding conditional betas, core characteristics, and equity risk exposure account for a stable share throughout the entire sample, which translates to their statistical significance in the majority of periods, as reported in the main text. Speculative demand characteristics contribute a larger share to estimated betas at the beginning and end of the sample, which is consistent with their strong statistical relevance in those periods and weak impact on risk compensation in the middle of the sample in early 2022. The contribution to daily or weekly betas of trading activity variables grows over time and remains one of the largest in the second half of the sample.

It is worth noting that the relative importance simply looks at a weighted sum of scaled coefficients. In contrast, the Wald-type bootstrap tests consider the raw estimates of $\Gamma_\alpha$ and $\Gamma_\beta$ to construct the Wald-type statistics for comparison with the bootstrap counterparts. Although this makes the comparison between the two sets of results more nuanced, the findings of both exercises align well with each other.

### Approximating the IPCA Factor Model

We approximate the IPCA latent factors with observable portfolios. We initially regress each IPCA factor on the value-weighted cryptocurrency market and all managed portfolios. Since some IPCA factors relate to similar characteristics, we then perform regularisation via elastic-net (Zou and Hastie, 2005) and allow at most two non-zero coefficients in each regression. This selection procedure identifies eleven characteristic-managed portfolios formed on {\tt capm $\beta$}, {\tt r21_1}, {\tt bm}, {\tt to}, {\tt bidask}, {\tt max $30$}, {\tt rvol}, {\tt down $\beta$}, {\tt equity capm $\beta$}, {\tt equity down $\beta$}, and the value-weighted cryptocurrency market. Figure A7 shows that these eleven portfolios jointly explain from 60% to 80% of the variation in IPCA factors. Table A4 compares the performance of the IPCA specification with models using selected characteristic-managed portfolios. IPCA achieves the highest explanatory power, followed by the approximate managed-portfolio specification, with observable factors performing substantially worse.

[Insert Figure A7 here]

[Insert Table A4 here]

### Asset Quality and Asset Pricing Performance on a Weekly Frequency

Table A5 reveals several important patterns that provide insights into where IPCA's modeling advantages are most pronounced. Examining the total $R^2$ performance in Panel A, IPCA shows stronger relative advantages for lower-quality cryptocurrencies. For highly volatile and illiquid assets (high {\tt ivol}, {\tt illiq}, {\tt bidask}), IPCA achieves 22--25% total $R^2$ compared to much lower performance from observable factors (14--16%), representing improvements of 33--35%. Similarly, for speculative assets with high lottery-like characteristics ({\tt max 30}), IPCA maintains 24% $R^2$ while observable factors achieve only 16%, a 33% performance gap. Conversely, for higher-quality assets characterized by large size, high trading volume, and low volatility, the performance differences narrow significantly, with observable factors achieving similar $R^2$ to IPCA.

[Insert Table A5 here]

The predictive $R^2$ results in Panel B reveal even more pronounced advantages for IPCA among lower-quality assets. For cryptocurrencies with poor liquidity characteristics, IPCA often achieves 2--4% predictive $R^2$ while alternative models struggle to reach 1%. The pattern is particularly clear for liquidity measures: IPCA achieves substantial predictive $R^2$ for illiquid assets (3--4%) while performing poorly for liquid assets, suggesting that mispricing is more predictable among less liquid cryptocurrencies. This finding aligns with the speculative demand patterns, where IPCA performs much better for high {\tt max 30} assets (3.76% vs 1.13% for observable factors).

### Volatility Scaling and Asset Pricing Performance

Table A6 shows that volatility scaling reduces but does not eliminate IPCA's outperformance. For daily returns, the gap in the total $R^2$ statistics between IPCA and the instrumented observable factors remains economically large and statistically significant at the 1% level. Importantly, the role of systematic mispricing persists after volatility scaling. The restricted IPCA model ($\Gamma_\alpha = 0$) shows a significant decline in predictive $R^2$ of 5.76% for daily returns, indicating that time-varying alphas continue to matter even when controlling for heteroskedasticity. This consistent pattern across all model types demonstrates that allowing for systematic mispricing is essential for explaining expected cryptocurrency returns, regardless of whether factors are latent or observable. The results for weekly returns show similar patterns. The performance differences remain statistically significant, and the importance of time-varying alphas persists, though the magnitudes are somewhat smaller.

[Insert Table A6 here]

These findings demonstrate that while extreme volatility contributes to IPCA's superior performance, the fundamental advantages of modeling systematic mispricing and using latent factors remain economically meaningful even in a more homoskedastic setting.

### Results for Individual Exchanges

To investigate whether IPCA's advantages are robust to data aggregation choices, we replicate the asset pricing analysis using data from four major exchanges: Binance, Coinbase, Kraken, and Bitfinex. Table A7 presents the results. For the exchange-level results, the ending date of May 1st, 2023, is common for all four exchanges, but the initial date is defined as follows: November 1st, 2019, for Binance; November 1st, 2021, for Coinbase; November 1st, 2021, for Kraken; and November 1st, 2018 for Bitfinex.

[Insert Table A7 here]

The analysis reveals that IPCA's outperformance becomes even more pronounced on individual exchanges. Performance gaps between IPCA and instrumented observable factors range from 30.5% (Kraken) to 58.7% (Bitfinex) in terms of total $R^2$, substantially larger than differences observed in aggregated data. IPCA achieves a total $R^2$ ranging from 50.5% (Bitfinex) to 69.3% (Kraken), indicating that volume-weighted aggregation may understate IPCA's true advantages by smoothing out pricing inefficiencies across venues.

Predictive $R^2$ results show striking cross-exchange heterogeneity. IPCA achieves predictive $R^2$ ranging from 0.13% to 0.58%, while instrumented observable factors perform well on some exchanges (0.68% on Coinbase) but poorly on others. The importance of modeling systematic mispricing also varies significantly: constraining alphas to zero reduces predictive $R^2$ by 63% on Bitfinex but a more modest 7% on Kraken.

### Augmented IPCA with Equity Factors

We consider the augmented IPCA specification:
$$
r_{i,t+1} = \alpha_{i,t}^{\prime} + \beta_{i,t}^{\prime}f_{t+1} + \delta_{i,t}^{\prime}g_{t+1} + \epsilon_{i,t+1},

$$
in which
$\alpha_{i,t}^{\prime}, \beta_{i,t}^{\prime},$ and
$\delta_{i,t}^{\prime}$ are time-varying coefficients instrumented with all cryptocurrency characteristics, $f_{t+1}$ and $g_{t+1}$
are the latent cryptocurrency factors and the equity factors, respectively. The loadings on observable factors are $\delta_{i,t}^{\prime}=\boldsymbol{z}_{i,t}^{\prime}\Gamma_{\delta} + \nu_{i,t+1}^{\delta},$ where $\Gamma_{\delta}$ is an $L\times M$ mapping from characteristics to factor coefficients and $\nu_{i,t+1}^{\delta}$ captures any idiosyncratic effect on the dynamics of factor exposures. The term $\delta_{i,t}^{\prime}g_{t+1}$
captures the portion of the return described by observable equity factors. The model with observable factors is mapped to the original IPCA by augmenting the factor specification to include $g_{t+1}$. Specifically, we rewrite equation ([eq:observable augmented]) as $r_{i,t+1} = z_{i,t}^\prime\tilde{\Gamma}\tilde{f}_{t+1} + \epsilon_{t+1}^*$, where $\tilde{f}_{t+1}=\left[1,\ f_{t+1}^{\prime}, g_{t+1}^{\prime}\right]^{\prime}$ and $\tilde{\Gamma}=\left[\Gamma_\alpha, \Gamma_\beta, \Gamma_\delta\right]$.

The first order condition for $\tilde{\Gamma}$ is the same as equation ([eq:IPCA2]) whereas the first-order condition for $f_{t+1}$ changes slightly to
$$
\begin{aligned}
f_{t+1}& = \left(\Gamma_\beta^{\prime}Z_t^{\prime}Z_t\Gamma_\beta\right)^{-1}\Gamma_\beta^{\prime}Z_t^{\prime}\left(r_{t+1}-Z_t\Gamma_\alpha-Z_t\Gamma_\delta g_{t+1}\right)\qquad\forall t.
\end{aligned}
$$
This is a cross-sectional regression of the returns in excess of mispricing and observable factor exposures on $\beta_t$. The panel variation in returns is allocated to latent factors extracted from cryptocurrency returns vis-á-vis observed risk factors that pertain to equity. Then, the incremental explanatory power of equity factors can be tested based on the null hypothesis $\mathcal{H}_0: \Gamma_\delta=\boldsymbol{0}_{L\times M}$ from which we construct a Wald-like test statistic as $W_\delta = \text{vec}\left(\widehat{\Gamma}_\delta\right)^{\prime}\text{vec}\left(\widehat{\Gamma}_\delta\right).$

The statistic $W_\delta$ measures the distance between the model with and without risk factors $g_{t+1}.$ If it is large relative to its bootstrap values, one can conclude that $g_{t+1}$ provides significant information on cryptocurrency returns. The p-value for the null hypothesis is obtained by a wild bootstrap method. First, we construct residuals of managed portfolios $\widehat{d}_{t+1}=Z_t^{\prime}\widehat{\epsilon}_{t+1}^{*}$
from the estimated model. Then, for each iteration $b$, we resample the portfolio returns imposing the null $\Gamma_\delta=0$. Next, we re-estimate $\Gamma_\delta$ for each bootstrap sample and construct the associated test statistic $\tilde{W}_\delta^b$. Finally, we compute the p-value as the fraction of $\tilde{W}_\delta^b$ exceeding $W_\delta$.

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

\newpage

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%


---

## Figures

**[FIGURE fig1]** Bootstrap Statistics for Daily Alphas over Time (4 sub-panels)
This figure illustrates the daily Wald-type test statistics (black line) and different percentiles of bootstrap statistics (grey areas) for the conditional alphas from an eight-factor IPCA model estimated on daily returns in a two-year rolling window.

**[FIGURE fig2]** Bootstrap Statistics for Weekly Alphas over Time (4 sub-panels)
This figure illustrates the weekly Wald-type test statistics (black line) and different percentiles of bootstrap statistics (grey areas) for the conditional alphas from an eight-factor IPCA model estimated on weekly returns in a two-year rolling window.

**[FIGURE fig3]** Bootstrap Statistics for Daily Betas over Time (4 sub-panels)
This figure illustrates the daily Wald-type test statistics (black line) and different percentiles of bootstrap statistics (grey areas) for the conditional betas from an eight-factor IPCA model estimated on daily returns in a two-year rolling window.

**[FIGURE fig4]** Bootstrap Statistics for Weekly Betas over Time (4 sub-panels)
This figure illustrates the weekly Wald-type test statistics (black line) and different percentiles of bootstrap statistics (grey areas) for the conditional betas from an eight-factor IPCA model estimated on weekly returns in a two-year rolling window.

**[FIGURE fig5]** Characteristic-Managed Portfolios and IPCA Latent Factors
Panel A shows the marginal $R^2,$ which are $R^2$ statistics from univariate regressions of each of the 35 characteristic-managed portfolios on each latent factor. Panel B shows the regression coefficients of a series of multivariate regressions in which all latent factors are projected onto each characteristic-managed portfolio.

**[FIGURE fig6]** Rolling-Window P-Values for Equity Factor Correlations
Panel A shows the p-values from rolling 2-year window regressions of IPCA factors F6 and F7 on the market factor (MKT). Panel B shows the p-values from rolling 2-year window regressions of the same factors on the value factor (HML). The dashed horizontal lines indicate conventional significance thresholds of 5% (red) and 10% (orange).

**[FIGURE appfig1]** Bootstrap Statistics for Daily Alphas over Time (6 sub-panels)
This figure illustrates the daily Wald-type test statistics (black line) and different percentiles of bootstrap statistics (grey areas) for the conditional alphas from an eight-factor IPCA model estimated on daily returns in a two-year rolling window.

**[FIGURE appfig2]** Bootstrap Statistics for Weekly Alphas over Time (6 sub-panels)
This figure illustrates the weekly Wald-type test statistics (black line) and different percentiles of bootstrap statistics (grey areas) for the conditional alphas from an eight-factor IPCA model estimated on weekly returns in a two-year rolling window.

**[FIGURE appfig3]** Bootstrap Statistics for Daily Betas over Time (5 sub-panels)
This figure illustrates the daily Wald-type test statistics (black line) and different percentiles of bootstrap statistics (grey areas) for the conditional betas from an eight-factor IPCA model estimated on daily returns in a two-year rolling window.

**[FIGURE appfig4]** Bootstrap Statistics for Weekly Betas over Time (5 sub-panels)
This figure illustrates the weekly Wald-type test statistics (black line) and different percentiles of bootstrap statistics (grey areas) for the conditional betas from an eight-factor IPCA model estimated on weekly returns in a two-year rolling window.

**[FIGURE appfig5]** Beta Bootstrap Test for Individual Characteristics
This figure summarises the results of the bootstrap test for the significance of individual characteristics in the IPCA specifications with eight latent factors. We report the bootstrap p-values for both daily and weekly returns.

**[FIGURE appfig6]** Relative Importance of Characteristics for Alphas and Betas over Time (4 sub-panels)
This figure illustrates the contributions of groups to the sum of squared alpha parameters and the weighted sum of squared beta parameters calculated based on daily or weekly returns. The figure reports the results for the IPCA model with eight factors and all characteristics used as instruments. { Panel A: Daily returns} { Panel B: Weekly returns}

**[FIGURE appfig7]** Approximating IPCA with Characteristic-Managed Portfolios
This figure illustrates the adjusted $R^2$ statistics from time-series regressions of IPCA factors on the set of eleven managed portfolios used to proxy the IPCA performance, as described in the main text.


## Tables

**[TABLE tab1]** Cryptocurrency Characteristics
This table defines 35 asset characteristics used in the empirical analysis. We group them into nine categories: market, size, and momentum; reversal; on-chain activity; trading activity; liquidity; speculative demand; volatility and downside risk; social media activity; and equity market exposure.

```latex
\begin{tabular}{lll}
\toprule 
\multicolumn{2}{l}{\bf Market, size, and momentum} & \\
(1) & {\tt capm $\beta$} & Crypto CAPM beta based on the previous 60 days of returns.\\ 
[.5em]
(2) & {\tt size} & Current available supply times the current USD price.\\
[.5em]
(3-5) & {\tt r*\_1} & Return from 14, 21, and 30 to one day before the prediction.\\
[.5em] 
\multicolumn{2}{l}{\bf Reversal} & \\
[.5em]
(6) & {\tt r2\_1}  & Short-term reversal (it is used only for a daily frequency \\
 &  & and is equivalent to r7\_1 on a weekly frequency).\\
 [.5em]
(7) & {\tt r7\_1} & Return from 7 to one day before prediction.\\
 [.5em]
(8) & {\tt r180\_60} & Return from 180 to 60 days before prediction.\\
[.5em]
(9) & {\tt rel\_to\_high} & Price to 90-day high price. \\
[.5em]
{\bf On-chain activity} & &\\
[.5em]
(10) & {\tt new\_add} & Number of unique addresses that appeared for the first time in a network.\\
[.5em]
(11) & {\tt act\_add} & Number of unique active addresses.\\
[.5em]
(12) & {\tt bm} & Network-to-marke value.\\
[.5em]
{\bf Trading activity} & &\\
[.5em]
(13) & {\tt \$vol} & Trading volume in \$.\\
[.5em]
(14) & {\tt to} & Last day's trading volume in \$ over the current market capitalization.\\
[.5em]
(15) & {\tt std\_vol} & Volatility of log-daily trading volume in the previous 30 days.\\
[.5em]
(16) & {\tt cv\_vol} & Volatility to mean of daily trading volume in the previous 30 days. \\
[.5em]
{\bf Liquidity} & &\\
[.5em]
(17) & {\tt bidask} & Average of daily bid-ask spreads.\\
[.5em]
(18) & {\tt illiq} & The 30-day average of daily ratios between the absolute return and volume.\\
[.5em]
(19) & {\tt vol\_shock} & Log daily trading volume minus its trend in the previous 30 days.\\
[.5em]
(20) & {\tt dto} & De-trended volume minus market turnover.\\
[.5em]
{\bf Speculative demand} & &\\
[.5em]
(21) & {\tt co-skew} & Crypto co-skewness based on the previous 60 days of returns.\\
[.5em]
(22) & {\tt max} $30$ & Maximum daily return in the previous 30 days.\\
[.5em]
(23) & {\tt max} $30 (4)$ & Average of the four highest daily returns in the previous 30 days.\\
[.5em]
(24) & {\tt rskew} & The realised skewness of daily returns in the previous 30 days. \\
[.5em]
\multicolumn{2}{l}{\bf Volatility and downside risk} &\\
[.5em]
(25) & {\tt ivol} & Volatility of crypto CAPM residuals based on the previous 60 days of returns.\\
[.5em]
(26) & {\tt rvol} & Realised volatility based on RiskMetrics with $\lambda=0.94$.\\
[.5em]
(27) & {\tt Downside $\beta$} & Crypto downside beta based on the previous 60 days of returns.\\
[.5em]
(28) & {\tt VaR(5\%)} & The historical Value-at-Risk at 5\% on the previous 90 daily returns.\\
[.5em]
{\bf Social media activity} & &\\
[.5em]
(29) & {\tt fb\_likes} & The daily number of cumulative Facebook likes. \\
[.5em]
(30) & {\tt reddit\_act} & The number of active Reddit subscribers in a day.\\
[.5em]
(31) & {\tt reddit\_posts} & The daily number of Reddit posts.\\
[.5em]
(32) & {\tt twitter\_f} & The daily number of Twitter followers.\\
[.5em]
{\bf Equity market exposure} & &\\
[.5em]
(33) & {\tt Equity capm $\beta$} & Equity CAPM beta based on the previous 60 days of returns.\\
[.5em]
(34) & {\tt Equity co-skew} & Equity co-skewness based on the previous 60 days of returns. \\
[.5em]
(35) & {\tt Equity downside $\beta$} & Equity downside beta based on the previous 60 days of returns.\\
\bottomrule
\end{tabular}
```

**[TABLE tab2]** Asset Pricing Performance
This table compares the in-sample and out-of-sample $R^2_{tot}$ and $R^2_{pred}$ reported in percentages for models with IPCA, observable, and PCA factors. The models are estimated on daily or weekly returns. For each model, it also displays the percentage change in $R^2_{tot}$ and $R^2_{pred}$ statistics relative to the unconstrained eight-factor IPCA model, where all characteristics are used as instruments. We highlight with $^*$ those performance differentials that are statistically significant at a 1% threshold level.

```latex
\begin{tabular}{lrrrrrrrrrr}
\multicolumn{11}{l}{\bf Panel A: \normalfont In-sample estimation}\\
\midrule 
&       & \multicolumn{4}{c}{Daily returns}     &       & \multicolumn{4}{c}{Weekly returns} \\
      \cmidrule{3-6}\cmidrule{8-11}
Method       & K& $R_{tot}^2$(\%)& $\Delta$(\%) & $R_{pred}^2$(\%) & $\Delta$(\%) &       & $R_{tot}^2$(\%) & $\Delta$(\%) & $R_{pred}^2$(\%) & $\Delta$(\%) \\
\midrule
{\tt IPCA8} (all characteristics) & 8     & 15.55 &       & 0.26  &       &       & 31.92 &       & 1.62  &  \\
{\tt IPCA8} (all characteristics) \& $\Gamma_\alpha = 0$ & 8     & 15.49 & -0.43$^*$ & 0.21  & -18.11$^*$ &       & 31.84 & -0.25 & 1.61  & -0.63 \\
      &       &       &       &       &       &       &       &       &       &  \\
Instrumented observable & 11    & 10.56 & -32.10$^*$ & 0.27  & 2.59  &       & 27.53 & -13.76$^*$ & 1.62  & 0.17 \\
Instrumented observable \& $\Gamma_\alpha = 0$ & 11    & 10.36 & -33.37$^*$ & 0.08  & -68.99$^*$ &       & 26.41 & -17.26$^*$ & 0.67  & -58.52$^*$ \\
      &       &       &       &       &       &       &       &       &       &  \\
{\tt PCA8} \& $\Gamma_\alpha = 0$ & 8     & 17.27 & 11.03$^*$ & 0.10  & -62.20$^*$ &       & 38.45 & 20.46$^*$ & 0.67  & -58.80$^*$ \\
\midrule 
\multicolumn{11}{l}{}\\

\multicolumn{11}{l}{\bf Panel B: \normalfont Out-of-sample estimation}\\
\midrule
      &       & \multicolumn{4}{c}{Daily returns}     &       & \multicolumn{4}{c}{Weekly returns} \\
      \cmidrule{3-6}\cmidrule{8-11}
      Method       & K& $R_{tot}^2$(\%)& $\Delta$(\%) & $R_{pred}^2$(\%) & $\Delta$(\%) &       & $R_{tot}^2$(\%) & $\Delta$(\%) & $R_{pred}^2$(\%) & $\Delta$(\%) \\
\midrule
{\tt IPCA8} (all characteristics) & 8     & 16.06 &       & 0.23  &       &       & 29.51 &       & 1.08  &  \\
{\tt IPCA8} (all characteristics) \& $\Gamma_\alpha = 0$ & 8     & 15.54 & -3.22$^*$ & 0.20  & -15.06$^*$ &       & 29.06 & -1.53$^*$ & 1.05  & -2.21 \\
      &       &       &       &       &       &       &       &       &       &  \\
Instrumented observable & 11    & 9.88  & -38.49$^*$ & 0.24  & 2.10  &       & 23.49 & -20.42$^*$ & 1.12  & 4.39$^*$ \\
Instrumented observable \& $\Gamma_\alpha = 0$ & 11    & 8.24  & -48.71$^*$ & 0.05  & -78.30$^*$ &       & 22.02 & -25.40$^*$ & 0.29  & -72.94$^*$ \\
      &       &       &       &       &       &       &       &       &       &  \\
{\tt PCA8} \& $\Gamma_\alpha = 0$ & 8     & 14.27 & -11.11$^*$ & -0.01 &  \multicolumn{1}{c}{-}     &       & 25.04 & -15.18$^*$ & -0.58 & \multicolumn{1}{c}{-} \\
\midrule 
\end{tabular}
```

**[TABLE tab3]** Pure-Alpha Portfolios
This table reports the out-of-sample performance of pure-alpha portfolios. Panel A (B) shows summary statistics for daily (weekly) estimation. Alphas are computed relative to the crypto CAPM, four-factor (F4), and eleven-factor (F11) models. The four-factor model employs the market, size, momentum, and value factors, whereas the eleven-factor specification additionally includes seven observable cryptocurrency factors selected in Section III.A.

```latex
\begin{tabular}{lrrrrrrrrr}
\multicolumn{10}{l}{\bf Panel A: \normalfont Daily returns}\\
\midrule
IPCA Factors & \multicolumn{1}{l}{Mean (\%)} & \multicolumn{1}{l}{Std (\%)} & \multicolumn{1}{l}{SR} & \multicolumn{1}{l}{$\alpha_{CAPM}(\%)$} & \multicolumn{1}{l}{$t_{CAPM}$} & \multicolumn{1}{l}{$\alpha_{F4}(\%)$} & \multicolumn{1}{l}{$t_{F4}$} & \multicolumn{1}{l}{$\alpha_{F11}(\%)$} & \multicolumn{1}{l}{$t_{F11}$} \\
\midrule 
$K=1$   & 1.412 & 1.951 & 0.724 & 1.411 & 7.450 & 1.282 & 6.863 & 1.064 & 5.811 \\
$K=2$   & 1.009 & 1.883 & 0.536 & 1.007 & 4.832 & 0.929 & 4.642 & 0.767 & 3.986 \\
$K=3$   & 1.064 & 1.772 & 0.601 & 1.063 & 5.625 & 0.983 & 5.420 & 0.809 & 4.679 \\
$K=4$   & 1.041 & 1.423 & 0.732 & 1.041 & 7.620 & 0.969 & 7.456 & 0.856 & 6.807 \\
$K=5$   & 0.949 & 1.206 & 0.787 & 0.949 & 8.192 & 0.889 & 7.881 & 0.786 & 7.086 \\
$K=6$   & 0.772 & 1.017 & 0.759 & 0.771 & 7.385 & 0.733 & 7.197 & 0.653 & 6.526 \\
$K=7$   & 0.573 & 0.800 & 0.717 & 0.573 & 7.426 & 0.541 & 7.347 & 0.482 & 6.496 \\
$K=8$   & 0.491 & 0.722 & 0.680 & 0.490 & 7.289 & 0.469 & 7.379 & 0.414 & 6.460 \\
\midrule
\multicolumn{10}{c}{}\\
\multicolumn{10}{l}{\bf Panel B: \normalfont Weekly returns}\\
\midrule
IPCA Factors & \multicolumn{1}{l}{Mean (\%)} & \multicolumn{1}{l}{Std (\%)} & \multicolumn{1}{l}{SR} & \multicolumn{1}{l}{$\alpha_{CAPM}(\%)$} & \multicolumn{1}{l}{$t_{CAPM}$} & \multicolumn{1}{l}{$\alpha_{F4}(\%)$} & \multicolumn{1}{l}{$t_{F4}$} & \multicolumn{1}{l}{$\alpha_{F11}(\%)$} & \multicolumn{1}{l}{$t_{F11}$} \\
\midrule 
$K=1$   & 1.092 & 1.485 & 0.736 & 1.086 & 12.791 & 1.083 & 12.977 & 1.072 & 15.456 \\
$K=2$   & 1.023 & 1.332 & 0.768 & 1.021 & 8.918 & 1.019 & 8.682 & 1.046 & 10.308 \\
$K=3$   & 1.002 & 1.343 & 0.746 & 1.002 & 7.603 & 1.002 & 7.465 & 1.026 & 9.163 \\
$K=4$   & 1.003 & 1.318 & 0.761 & 1.002 & 8.987 & 1.002 & 8.711 & 1.027 & 10.708 \\
$K=5$   & 0.953 & 1.229 & 0.775 & 0.953 & 9.098 & 0.951 & 8.710 & 0.973 & 10.673 \\
$K=6$   & 0.875 & 1.085 & 0.807 & 0.879 & 9.371 & 0.873 & 9.073 & 0.883 & 11.589 \\
$K=7$   & 0.765 & 1.043 & 0.734 & 0.768 & 8.074 & 0.764 & 7.730 & 0.771 & 10.407 \\
$K=8$   & 0.746 & 0.977 & 0.764 & 0.748 & 10.363 & 0.741 & 9.854 & 0.755 & 13.964 \\
\midrule 
\end{tabular}
```

**[TABLE tab4]** Characteristics and Systematic Mispricing
This table reports p-values for the $\Gamma_\alpha^g = 0$ test in models with different numbers of factors, using all characteristics as instruments. The table shows the results for models estimated on daily and weekly returns.

```latex
\begin{tabular}{lrrrrrrrrr}
\bf Panel A: \normalfont Daily returns &  &  \\
\midrule
Groups& \multicolumn{1}{l}{L} &  \multicolumn{8}{c}{Number of factors} \\
\cmidrule{3-10}
&    &  1     & 2     & 3     & 4     & 5     & 6     & 7     & 8 \\
\midrule         
All characteristics & 35    & 0.00  & 0.00  & 0.00  & 0.00  & 0.00  & 0.01  & 0.01  & 0.03 \\
[0.5em]
Market, size and momentum & 5     & 0.00  & 0.00  & 0.01  & 0.54  & 0.32  & 0.43  & 0.64  & 0.95 \\
Reversal & 9     & 0.00  & 0.01  & 0.06  & 0.10  & 0.14  & 0.15  & 0.19  & 0.25 \\
On-chain activity & 8     & 0.04  & 0.17  & 0.46  & 0.48  & 0.48  & 0.63  & 0.73  & 0.63 \\
Trading activity & 9     & 0.03  & 0.56  & 0.68  & 0.48  & 0.49  & 0.95  & 0.99  & 0.98 \\
Liquidity & 9     & 0.00  & 0.00  & 0.00  & 0.00  & 0.00  & 0.00  & 0.00  & 0.00 \\
Speculative demand & 9     & 0.00  & 0.00  & 0.00  & 0.00  & 0.00  & 0.02  & 0.05  & 0.04 \\
Volatility and downside risk & 9     & 0.00  & 0.01  & 0.00  & 0.03  & 0.07  & 0.19  & 0.37  & 0.82 \\
Social media activity & 9     & 0.00  & 0.00  & 0.00  & 0.01  & 0.04  & 0.23  & 0.19  & 0.10 \\
Equity market exposure& 8     & 0.22  & 0.40  & 0.43  & 0.52  & 0.52  & 0.93  & 0.96  & 0.89 \\
\midrule
\multicolumn{10}{c}{}\\
\bf Panel B: \normalfont Weekly returns &  &  \\
\midrule
Groups& \multicolumn{1}{l}{L} &  \multicolumn{8}{c}{Number of factors} \\
\cmidrule{3-10}
&    &  1     & 2     & 3     & 4     & 5     & 6     & 7     & 8 \\
\midrule     
All characteristics & 34    & 0.00  & 0.00  & 0.00  & 0.00  & 0.00  & 0.00  & 0.00  & 0.00 \\
[0.5em]
Market, size and momentum & 5     & 0.00  & 0.00  & 0.00  & 0.00  & 0.00  & 0.07  & 0.32  & 0.69 \\
Reversal & 8     & 0.00  & 0.00  & 0.00  & 0.00  & 0.00  & 0.00  & 0.00  & 0.00 \\
On-chain activity & 8     & 0.22  & 0.19  & 0.21  & 0.07  & 0.07  & 0.16  & 0.24  & 0.54 \\
Trading activity & 9     & 0.58  & 0.70  & 0.67  & 0.47  & 0.49  & 0.59  & 0.70  & 0.82 \\
Liquidity & 9     & 0.03  & 0.02  & 0.02  & 0.01  & 0.02  & 0.16  & 0.10  & 0.08 \\
Speculative demand & 9     & 0.12  & 0.04  & 0.02  & 0.01  & 0.10  & 0.07  & 0.06  & 0.02 \\
Volatility and downside risk & 9     & 0.32  & 0.25  & 0.31  & 0.24  & 0.44  & 0.37  & 0.21  & 0.12 \\
Social media activity & 9     & 0.07  & 0.08  & 0.11  & 0.14  & 0.10  & 0.09  & 0.47  & 0.39 \\
Equity market exposure& 8     & 0.97  & 0.80  & 0.81  & 0.77  & 0.85  & 0.34  & 0.34  & 0.25 \\
\midrule
\end{tabular}
```

**[TABLE tab5]** Characteristics and Risk Compensation
This table reports p-values for the $\Gamma_\beta^g = 0$ test in the models with different numbers of factors where all characteristics are used as instruments. The table shows the results for the models estimated on daily (Panel A) or weekly (Panel B) returns.

```latex
\begin{tabular}{lrrrrrrrrr}
\bf Panel A: \normalfont Daily returns &  &  \\
\midrule
Groups& \multicolumn{1}{l}{L} &  \multicolumn{8}{c}{Number of factors} \\
\cmidrule{3-10}
&    &  1     & 2     & 3     & 4     & 5     & 6     & 7     & 8 \\
\midrule
Market, size and momentum & 5     & 0.00  & 0.08  & 0.05  & 0.01  & 0.02  & 0.04  & 0.05  & 0.04 \\
Reversal & 9     & 0.01  & 0.21  & 0.62  & 0.22  & 0.19  & 0.38  & 0.54  & 0.75 \\
On-chain activity & 8     & 0.06  & 0.29  & 0.61  & 0.80  & 0.93  & 0.99  & 0.96  & 0.99 \\
Trading activity & 9     & 0.19  & 0.67  & 0.47  & 0.79  & 0.91  & 0.63  & 0.35  & 0.42 \\
Liquidity & 9     & 0.18  & 0.05  & 0.23  & 0.41  & 0.61  & 0.71  & 0.67  & 0.51 \\
Speculative demand & 9     & 0.31  & 0.15  & 0.03  & 0.02  & 0.04  & 0.05  & 0.08  & 0.01 \\
Volatility and downside risk & 9     & 0.00  & 0.59  & 0.44  & 0.21  & 0.04  & 0.02  & 0.01  & 0.01 \\
Social media activity & 9     & 0.01  & 0.27  & 0.68  & 0.82  & 0.92  & 0.94  & 0.98  & 1.00 \\
Equity market exposure & 8     & 0.80  & 0.83  & 0.88  & 1.00  & 0.21  & 0.04  & 0.00  & 0.00 \\
\midrule
\multicolumn{10}{c}{}\\
\bf Panel B: \normalfont Weekly returns &  &  \\
\midrule
Groups& \multicolumn{1}{l}{L} &  \multicolumn{8}{c}{Number of factors} \\
\cmidrule{3-10}
&    &  1     & 2     & 3     & 4     & 5     & 6     & 7     & 8 \\
\midrule
Market, size and momentum & 5     & 0.13  & 0.02  & 0.00  & 0.01  & 0.03  & 0.01  & 0.00  & 0.00 \\
Reversal & 8     & 0.01  & 0.07  & 0.13  & 0.11  & 0.09  & 0.02  & 0.05  & 0.00 \\
On-chain activity & 8     & 0.12  & 0.82  & 0.68  & 0.08  & 0.17  & 0.24  & 0.07  & 0.00 \\
Trading activity & 9     & 0.09  & 0.28  & 0.49  & 0.29  & 0.00  & 0.06  & 0.01  & 0.02 \\
Liquidity & 9     & 0.25  & 0.38  & 0.64  & 0.68  & 0.42  & 0.25  & 0.49  & 0.65 \\
Speculative demand & 9     & 0.40  & 0.76  & 0.53  & 0.62  & 0.40  & 0.68  & 0.25  & 0.26 \\
Volatility and downside risk & 9     & 0.05  & 0.76  & 0.76  & 0.79  & 0.95  & 0.90  & 0.84  & 0.79 \\
Social media activity & 9     & 0.04  & 0.46  & 0.62  & 0.88  & 0.85  & 0.54  & 0.65  & 0.49 \\
Equity market exposure & 8     & 0.65  & 0.65  & 0.41  & 0.61  & 0.62  & 0.20  & 0.44  & 0.44 \\
\midrule
\end{tabular}
```

**[TABLE tab6]** Asset Quality and Asset Pricing Performance
This table reports $R^2_{tot}$ (Panel A) and $R^2_{pred}$ (Panel B) in percentages for models with IPCA, observable, or PCA factors by cryptocurrency groups sorted on selected characteristics. $\Delta L(\%)$ and $\Delta H(\%)$ show the percentage difference in $R^2$ between each alternative model and IPCA for low and high quartiles, respectively. Negative values indicate IPCA outperforms the alternative model. The models are estimated on daily returns.

```latex
\begin{tabular}{lrrrrrrrrrrrr}
\multicolumn{13}{l}{\bf Panel A: \normalfont $R_{tot}^2 (\%)$}\\
\midrule 
& \multicolumn{2}{c}{IPCA} &       & \multicolumn{4}{c}{Instrumented observable factors}       &       & \multicolumn{4}{c}{Static PCA}  \\
\cmidrule{2-3}\cmidrule{5-8}\cmidrule{10-13}
  & \multicolumn{1}{r}{Low} & \multicolumn{1}{r}{High} &       & \multicolumn{1}{r}{Low} & \multicolumn{1}{r}{High} & $\Delta$L(\%) & $\Delta$H(\%) &       & \multicolumn{1}{r}{Low} & \multicolumn{1}{r}{High} & $\Delta$L(\%) & $\Delta$H(\%) \\
  \midrule 
{\tt capm $\beta$} & 12.11 & 16.61 &       & 5.46  & 10.77 & -55   & -35   &       & 14.68 & 18.58 & 21    & 12 \\
{\tt size} & 12.75 & 25.04 &       & 5.64  & 26.28 & -56   & 5     &       & 13.14 & 27.45 & 3     & 10 \\
{\tt new\_add} & 13.18 & 22.30 &       & 6.98  & 20.34 & -47   & -9    &       & 13.27 & 23.51 & 1     & 5 \\
{\tt act\_add} & 12.88 & 22.82 &       & 7.13  & 21.07 & -45   & -8    &       & 14.04 & 24.36 & 9     & 7 \\
{\tt bm}   & 18.37 & 13.72 &       & 16.78 & 6.48  & -9    & -53   &       & 21.78 & 14.06 & 19    & 2 \\
          &       &       &       &       &       &       &       &       &       &       &       &  \\
{\tt \$vol} & 12.30 & 26.28 &       & 4.86  & 25.74 & -61   & -2    &       & 13.62 & 28.37 & 11    & 8 \\
{\tt bidask} & 21.95 & 12.54 &       & 18.42 & 5.24  & -16   & -58   &       & 25.46 & 13.42 & 16    & 7 \\
{\tt ivol} & 36.94 & 12.02 &       & 37.93 & 4.40  & 3     & -63   &       & 41.33 & 14.17 & 12    & 18 \\
{\tt illiq} & 32.25 & 12.04 &       & 33.08 & 4.54  & 3     & -62   &       & 35.86 & 13.87 & 11    & 15 \\
{\tt VaR(5\%)} & 11.78 & 24.39 &       & 4.65  & 23.25 & -61   & -5    &       & 14.20 & 29.44 & 21    & 21 \\
          &       &       &       &       &       &       &       &       &       &       &       &  \\
{\tt max} $30$ & 29.43 & 11.57 &       & 29.30 & 5.03  & 0     & -57   &       & 32.57 & 13.66 & 11    & 18 \\
{\tt reddit\_act} & 12.89 & 27.86 &       & 7.82  & 26.96 & -39   & -3    &       & 13.74 & 29.19 & 7     & 5 \\
{\tt reddit\_post} & 12.38 & 26.89 &       & 7.25  & 26.77 & -41   & 0     &       & 11.88 & 29.23 & -4    & 9 \\
{\tt twitter\_f} & 13.66 & 23.02 &       & 7.61  & 20.71 & -44   & -10   &       & 14.67 & 24.18 & 7     & 5 \\
          &       &       &       &       &       &       &       &       &       &       &       &  \\
{\tt Equity capm $\beta$} & 12.89 & 15.23 &       & 6.73  & 8.89  & -48   & -42   &       & 14.90 & 17.33 & 16    & 14 \\
\midrule
          &       &       &       &       &       &       &       &       &       &       &       &  \\
\multicolumn{13}{l}{\bf Panel B: \normalfont $R_{pred}^2 (\%)$}\\
\midrule 
& \multicolumn{2}{c}{IPCA} &       & \multicolumn{4}{c}{Instrumented observable factors}       &       & \multicolumn{4}{c}{Static PCA}  \\

\cmidrule{2-3}\cmidrule{5-8}\cmidrule{10-13}
  & \multicolumn{1}{r}{Low} & \multicolumn{1}{r}{High} &       & \multicolumn{1}{r}{Low} & \multicolumn{1}{r}{High} & $\Delta$L(\%) & $\Delta$H(\%) &       & \multicolumn{1}{r}{Low} & \multicolumn{1}{r}{High} & $\Delta$L(\%) & $\Delta$H(\%) \\
  \midrule 
{\tt capm $\beta$} & 0.38  & 0.31  &       & 0.10  & 0.08  & -73   & -73   &       & 0.16  & 0.15  & -58   & -51 \\
{\tt size}& 0.44  & -0.14 &       & 0.11  & 0.11  & -75   & -   &       & 0.14  & 0.05  & -68   & - \\
{\tt new\_add} & 0.23  & 0.06  &       & 0.05  & 0.08  & -78   & 37    &       & 0.00  & 0.06  & -102  & -8 \\
{\tt act\_add} & 0.30  & 0.03  &       & 0.08  & 0.08  & -74   & 151   &       & 0.08  & 0.07  & -73   & 121 \\
{\tt bm}    & 0.03  & 0.48  &       & 0.09  & 0.13  & 223   & -73   &       & 0.14  & 0.14  & 388   & -72 \\
          &       &       &       &       &       &       &       &       &       &       &       &  \\
{\tt \$vol} & 0.45  & -0.11 &       & 0.12  & 0.05  & -73   & 147   &       & 0.16  & 0.03  & -65   & - \\
{\tt bidask} & -0.18 & 0.58  &       & 0.04  & 0.12  & -   & -79   &       & 0.19  & 0.09  & -   & -84 \\
{\tt ivol}  & -0.66 & 0.42  &       & -0.03 & 0.10  & -    & -76   &       & -0.07 & 0.17  & -    & -59 \\
{\tt illiq} & -0.39 & 0.42  &       & 0.04  & 0.11  & -   & -75   &       & 0.03  & 0.17  & -   & -61 \\
{\tt VaR(5\%)} & 0.43  & -0.24 &       & 0.11  & 0.03  & -75   & -   &       & 0.17  & 0.14  & -60   & - \\
          &       &       &       &       &       &       &       &       &       &       &       &  \\
{\tt max} $30$ & -0.15 & 0.40  &       & 0.04  & 0.09  & -   & -78   &       & -0.01 & 0.10  & -    & -75 \\
{\tt reddit\_act} & 0.30  & -0.02 &       & 0.08  & 0.06  & -73   & -   &       & 0.13  & 0.01  & -57   & - \\
{\tt reddit\_post} & 0.37  & -0.19 &       & 0.09  & 0.04  & -75   & -   &       & 0.09  & 0.04  & -76   & - \\
{\tt twitter\_f} & 0.31  & 0.09  &       & 0.08  & 0.07  & -74   & -18   &       & 0.09  & 0.06  & -71   & -34 \\
          &       &       &       &       &       &       &       &       &       &       &       &  \\
{\tt Equity capm $\beta$} & 0.32  & 0.39  &       & 0.08  & 0.11  & -77   & -72   &       & 0.16  & 0.12  & -51   & -69 \\
\midrule 
\end{tabular}
```

**[TABLE tab7]** IPCA-Based Tests for Equity Factors
The table reports p-values for the test $\Gamma_\delta = 0$ on instrumented loadings of equity factors when those are included with IPCA factors. We employ all characteristics as instruments for latent and observable factor loadings. The left panel reports the p-values of beta loadings when equity factors are included one at a time, whereas the right panel reports the p-values of beta loadings when all equity factors are included jointly in the estimation.

```latex
\begin{tabular}{lrrrrrrrrrrrrr}
\midrule 
IPCA& \multicolumn{6}{c}{Individual Tests} & & \multicolumn{6}{c}{Joint Tests}\\
\cmidrule{2-7}\cmidrule{9-14}
& MKT & SMB & HML & RMW & CMA & MOM & & MKT & SMB & HML & RMW & CMA & MOM \\
\midrule    
$K=1$     & 0.79  & 0.98  & 0.60  & 0.66  & 0.97  & 0.49  & & 0.71  & 0.60  & 0.21  & 0.48  & 0.44  & 0.40  \\
$K=2$     & 0.71  & 0.97  & 0.59  & 0.43  & 0.92  & 0.27  & & 0.68  & 0.92  & 0.47  & 0.34  & 0.74  & 0.08  \\
$K=3$     & 0.70  & 0.90  & 0.42  & 0.15  & 0.94  & 0.15  & & 0.58  & 0.90  & 0.34  & 0.72  & 0.96  & 0.08  \\
$K=4$     & 0.51  & 0.94  & 0.29  & 0.27  & 0.91  & 0.25  & & 0.68  & 0.98  & 0.24  & 0.39  & 0.71  & 0.17  \\
$K=5$     & 0.65  & 0.85  & 0.16  & 0.26  & 0.88  & 0.17  & & 0.54  & 0.91  & 0.23  & 0.35  & 0.65  & 0.05  \\
$K=6$     & 0.65  & 0.67  & 0.03  & 0.20  & 0.84  & 0.11  & & 0.71  & 0.78  & 0.03  & 0.31  & 0.56  & 0.09  \\
$K=7$     & 0.57  & 0.57  & 0.06  & 0.22  & 0.73  & 0.07  & & 0.61  & 0.80  & 0.12  & 0.31  & 0.69  & 0.01  \\
$K=8$     & 0.50  & 0.47  & 0.02  & 0.33  & 0.76  & 0.46  & & 0.70  & 0.77  & 0.06  & 0.34  & 0.67  & 0.06  \\
\bottomrule
\end{tabular}
```

**[TABLE tab8]** Factor-Spanning Regressions
This table reports the results of factor-spanning regressions, in which we regress each latent factor from the eight-factor IPCA model on equity factors. We label with $^{***}, ^{**}, ^{*}$ those coefficients significant at the 1%, 5%, 10% confidence levels based on robust standard errors.

```latex
\begin{tabular}{lrrrrrrrrrrrrrrrrr}
\toprule
IPCA factors       &       & \multicolumn{1}{r}{F1} &       & \multicolumn{1}{r}{F2} &       & \multicolumn{1}{r}{F3} &       & \multicolumn{1}{r}{F4} &       & \multicolumn{1}{r}{F5} &       & \multicolumn{1}{r}{F6} &       & \multicolumn{1}{r}{F7} &       & \multicolumn{1}{r}{F8} &  \\
\midrule 
& \multicolumn{1}{l}{$\alpha(\%)$} & 0.10  &       & 1.60  & \multicolumn{1}{l}{***} & 0.60  & \multicolumn{1}{l}{***} & 2.50  & \multicolumn{1}{l}{***} & 0.20  &       & 0.70  & \multicolumn{1}{l}{***} & 0.20  &       & 1.40  & \multicolumn{1}{l}{***} \\
[1em]
& \multicolumn{1}{l}{MKT} & 0.30  &       & -0.30 &       & -0.40 & \multicolumn{1}{l}{*} & 0.00  &       & 0.10  &       & -0.40 & \multicolumn{1}{l}{***} & -1.20 & \multicolumn{1}{l}{***} & 0.00  &  \\
& \multicolumn{1}{l}{SMB} & -0.50 &       & -0.50 &       & -0.70 & \multicolumn{1}{l}{*} & 0.50  &       & 0.00  &       & 0.00  &       & -0.20 &       & 0.20  &  \\
Equity      & \multicolumn{1}{l}{HML} & 0.40  &       & 0.60  &       & 0.70  & \multicolumn{1}{l}{**} & -0.30 &       & 0.10  &       & -0.30 &       & 0.40  & \multicolumn{1}{l}{**} & 0.10  &  \\
& \multicolumn{1}{l}{RMW} & -0.20 &       & -0.90 &       & 0.10  &       & -0.10 &       & -0.10 &       & 0.20  &       & 0.40  &       & 0.00  &  \\
& \multicolumn{1}{l}{CMA} & -0.80 &       & -1.20 &       & -0.70 &       & 0.30  &       & -0.40 &       & 0.40  &       & -0.40 &       & -0.20 &  \\
& \multicolumn{1}{l}{MOM} & -0.20 &       & -0.40 &       & 0.10  &       & -0.20 &       & 0.00  &       & 0.00  &       & 0.00  &       & 0.00  &  \\
[1em]
Adj. $R^2$(\%) &       & -0.20 &       & 0.00  &       & 0.40  &       & -0.10 &       & -0.30 &       & 0.70  &       & 9.10  &       & -0.20 &  \\
\bottomrule 
\end{tabular}
```

**[TABLE apptab1]** Summary Statistics
This table reports the number of coins, mean, median, and sum of market capitalization of cryptocurrencies by year. The last column displays the ratio of market capitalization in our sample to the total market capitalization of all available cryptocurrencies. The number of coins refers to the total number of cryptocurrencies traded within a year, whereas market capitalization statistics are end-of-year observations for all years except 2023, when the sample stops in May.

```latex
\begin{tabular}{lrrrrrr}
\toprule
Year  & \multicolumn{1}{l}{\# coins} &    \multicolumn{4}{c}{Market capitalisation (\$mil)}\\ \cmidrule{3-6}  
 &  &   Mean & Median & Sum & Ratio \\
\midrule 
2016  & 11    & 80.42 & 1485.39 & 16640.36 & 93.06 \\
2017  & 203   & 45.68 & 1781.26 & 478245.33 & 83.61 \\
2018  & 553   & 22.78 & 749.58 & 111850.30 & 86.71 \\
2019  & 578   & 7.13  & 435.46 & 168585.59 & 85.58 \\
2020  & 527   & 4.37  & 756.66 & 674055.74 & 92.08 \\
2021  & 355   & 13.77 & 5065.21 & 1543210.82 & 70.79 \\
2022  & 289   & 13.76 & 4490.17 & 505259.46 & 63.32 \\
2023  & 210   & 19.15 & 4595.67 & 864364.51 & 71.44 \\
Full  & 630   & 10.73 & 1929.20 &       &       &  \\
\bottomrule
\end{tabular}
```

**[TABLE apptab2]** Summary Statistics for Daily Returns of Individual Cryptocurrencies
This table reports selected percentiles of summary statistics for daily returns of individual cryptocurrencies. For each asset, we first compute the mean, standard deviation, maximum, median, minimum, Sharpe ratio, skewness, and kurtosis statistics using the time series of daily returns. Then, we calculate the selected percentiles (0 (Min), 10, 25, 50, 75, 90, and 100 (Max)) across cryptocurrencies. The Sharpe ratio is converted to a weekly basis by multiplying by $\sqrt{7}$, whereas other statistics are reported in daily terms.

```latex
\begin{tabular}{lrrrrrrrr}
\toprule 
Percentile & Mean (\%)& Std (\%) & Max (\%) & Med (\%) & Min (\%) & SR & Skew & Kurt \\
\midrule
0 (Min)   & -7.088 & 1.304 & 4.149 & -18.337 & -99.960 & -0.797 & -2.740 & 1.339 \\
10  & -0.964 & 7.673 & 46.265 & -0.853 & -98.286 & -0.180 & -0.342 & 4.994 \\
25  & -0.467 & 9.799 & 71.054 & -0.499 & -93.645 & -0.084 & 0.094 & 7.242 \\
50  & -0.159 & 13.933 & 100.099 & -0.256 & -82.401 & -0.035 & 0.464 & 10.940 \\
75  & 0.030  & 21.531 & 129.763 & -0.036 & -64.344 & 0.006 & 0.946 & 15.896 \\
90  & 0.652 & 30.816 & 142.992 & 0.075 & -49.317 & 0.086 & 1.527 & 24.136 \\
100 (Max)   & 12.65 & 98.432 & 149.967 & 9.241 & -2.279 & 0.647 & 5.293 & 102.940 \\
\bottomrule
\end{tabular}
```

**[TABLE apptab3]** Summary Statistics for Observable Factors
This table reports summary statistics of the cryptocurrency market returns and observable risk factors. Each day, we sort cryptocurrencies into quintiles based on asset characteristics, one at a time, and form a long-short portfolio that buys (sells) cryptocurrencies in the top (bottom) quintile of each characteristic. The mean, standard deviation, maximum, median, and minimum, skewness, and kurtosis statistics are reported in daily terms, whereas the Sharpe ratio is converted to a weekly basis by multiplying by $\sqrt{7}$.

```latex
\begin{tabular}{lrrrrrrrr}
\toprule 
Factor & Mean (\%)& Std (\%) & Max (\%) & Med (\%) & Min (\%) & SR & Skew & Kurt \\
\midrule
mkt$\_$vw & 0.024 & 4.176 & 15.656 & 0.108 & -49.561 & 0.015 & -1.263 & 11.982 \\
{\tt size} & -0.464 & 3.754 & 17.851 & -0.277 & -41.341 & -0.327 & -1.068 & 9.657 \\
{\tt r14\_1} & 0.249 & 6.547 & 55.947 & 0.213 & -57.393 & 0.101 & 0.024 & 13.639 \\
{\tt r21\_1} & 0.226 & 6.246 & 54.415 & 0.182 & -58.335 & 0.096 & 0.068 & 16.842 \\
{\tt r30\_1} & 0.057 & 5.779 & 53.523 & 0.131 & -55.103 & 0.026 & -0.926 & 19.068 \\
\midrule
{\tt r2\_1} & -0.039 & 6.589 & 42.927 & -0.001 & -75.261 & -0.016 & -0.735 & 14.025 \\
{\tt r7\_1} & 0.111 & 6.633 & 49.760 & 0.218 & -66.253 & 0.044 & -1.250 & 17.940 \\
{\tt r180\_60} & 0.151 & 4.598 & 34.188 & 0.109 & -36.993 & 0.087 & -0.333 & 11.640 \\
{\tt rel\_to\_high} & 0.487 & 6.091 & 84.219 & 0.484 & -69.145 & 0.211 & 0.386 & 34.700 \\
\midrule
{\tt new\_add} & -0.023 & 5.824 & 46.098 & 0.204 & -67.357 & -0.011 & -2.879 & 34.938 \\
{\tt act\_add} & 0.100 & 5.753 & 27.229 & 0.343 & -72.864 & 0.046 & -3.047 & 31.018 \\
{\tt bm} & 0.182 & 4.596 & 43.931 & 0.023 & -45.532 & 0.105 & 0.639 & 19.568 \\
\midrule
{\tt \$vol} & 0.678 & 8.328 & 83.276 & 0.372 & -61.172 & 0.215 & 0.485 & 15.877 \\
{\tt to} & 0.064 & 6.708 & 55.901 & 0.003 & -53.787 & 0.025 & 0.281 & 17.324 \\
{\tt std\_vol} & -0.528 & 6.311 & 67.391 & -0.492 & -76.679 & -0.221 & -0.319 & 28.838 \\
{\tt cv\_vol} & -0.417 & 7.245 & 77.258 & -0.464 & -79.522 & -0.152 & 1.066 & 26.609 \\
\midrule
{\tt bidask} & -0.688 & 8.972 & 79.577 & -0.967 & -84.696 & -0.203 & 0.748 & 17.056 \\
{\tt illiq} & -0.562 & 8.798 & 87.684 & -0.279 & -81.492 & -0.169 & -0.219 & 16.608 \\
{\tt vol\_shock} & -0.040 & 4.505 & 44.971 & -0.154 & -44.167 & -0.023 & 0.295 & 14.868 \\
{\tt dto} & -0.089 & 4.405 & 43.994 & -0.138 & -43.891 & -0.054 & -0.161 & 18.572 \\
\midrule 
{\tt co-skew} & -0.336 & 5.854 & 48.841 & -0.169 & -78.566 & -0.152 & -1.267 & 30.739 \\
{\tt max30} & -1.037 & 7.903 & 72.592 & -0.915 & -83.895 & -0.347 & -0.429 & 18.508 \\
{\tt max30 (4)} & -1.277 & 7.906 & 49.316 & -1.065 & -84.596 & -0.427 & -1.081 & 13.167 \\
\midrule
{\tt ivol} & -0.786 & 8.390 & 66.591 & -0.701 & -67.634 & -0.248 & -0.102 & 9.531 \\
{\tt rvol} & -1.280 & 9.199 & 60.680 & -1.199 & -87.319 & -0.368 & -0.232 & 10.205 \\
{\tt rskew} & -0.480 & 5.059 & 51.749 & -0.239 & -62.388 & -0.251 & -1.834 & 30.471 \\
{\tt Downside $\beta$} & -0.191 & 6.233 & 70.560 & -0.200 & -54.768 & -0.081 & 0.751 & 21.253 \\
{\tt VaR(5\%)} & 0.737 & 7.933 & 65.333 & 0.510 & -53.207 & 0.246 & 0.327 & 7.558 \\
\midrule
{\tt fb\_likes} & 0.446 & 5.145 & 32.341 & 0.537 & -94.976 & 0.229 & -4.100 & 69.353 \\
{\tt reddit\_act} & 0.334 & 6.094 & 58.886 & 0.250 & -90.218 & 0.145 & -1.330 & 38.021 \\
{\tt reddit\_posts} & 0.251 & 5.956 & 37.871 & 0.302 & -80.465 & 0.111 & -2.595 & 38.696 \\
{\tt twitter\_f} & 0.190 & 4.808 & 70.493 & 0.200 & -45.611 & 0.105 & 0.876 & 46.061 \\
\midrule
{\tt Equity capm $\beta$} & 0.014 & 6.460 & 65.446 & -0.046 & -82.611 & 0.006 & -1.382 & 31.783 \\
{\tt Equity co-skew} & -0.066 & 4.841 & 51.767 & -0.093 & -53.488 & -0.036 & 0.453 & 18.188 \\
{\tt Equity downside $\beta$} & 0.142 & 6.840 & 77.374 & 0.124 & -78.777 & 0.055 & 0.029 & 25.222 \\
\bottomrule
\end{tabular}
```

**[TABLE apptab4]** IPCA versus Instrumented Characteristic-Managed Portfolios
This table compares the in-sample and out-of-sample $R^2_{tot}$ and $R^2_{pred}$ for models with IPCA factors, observable factors, or selected managed portfolios. We highlight with $^*$ those performance differentials which are statistically significant at a 1% threshold level.

```latex
\begin{tabular}{lrrrrrrrrrrr}
\toprule 
          &       & \multicolumn{4}{c}{In-sample}     &       & \multicolumn{4}{c}{Out-of-sample} \\
          \cmidrule{3-6}\cmidrule{8-11}
   Benchmarks       & K& $R_{tot}^2$(\%)& $\Delta$(\%) & $R_{pred}^2$(\%) & $\Delta$(\%) &       & $R_{tot}^2$(\%) & $\Delta$(\%) & $R_{pred}^2$(\%) & $\Delta$(\%) \\
          \midrule 
    {\tt IPCA8} with $z = \left\{\text{all characteristics}\right\}$ & 8     & 15.55 &       & 0.26  &       &       & 16.06 &       & 0.23  &  \\
    {\tt IPCA8} with $z = \left\{\text{all characteristics}\right\} (\Gamma_\alpha = 0)$ & 8     & 15.49 & -0.43$^*$ & 0.21  & -18.11$^*$ &       & 15.54 & -3.22$^*$ & 0.20  & -15.06$^*$ \\
          &       &       &       &       &       &       &       &       &       &  \\
Instrumented observable & 11    & 10.56 & -32.10$^*$ & 0.27  & 2.59  &       &  9.88 & -38.49$^*$ & 0.24  &  2.10 \\      
Instrumented observable \& Gamma = 0 & 11    & 10.36 & -33.37$^*$ & 0.08  & -68.99$^*$ &       &  8.24 & -48.71$^*$ & 0.05  & -78.30$^*$ \\
          &       &       &       &       &       &       &       &       &       &  \\
Instrumented managed portfolios & 11    & 13.99 & -10.09$^*$ & 0.26  & 1.29  &       & 14.11 & -12.15$^*$ & 0.23  & -2.05 \\
Instrumented managed portfolios \& Gamma = 0 & 11    & 13.89 & -10.68$^*$ & 0.18  & -31.31$^*$ &       & 14.01 & -12.72$^*$ & 0.18  & -23.05$^*$ \\
 \midrule 
\end{tabular}
```

**[TABLE apptab5]** Asset Quality and Pricing Performance for Weekly Returns
This table reports $R^2_{tot}$ (Panel A) and $R^2_{pred}$ (Panel B) in percentages for models with IPCA, observable, or PCA factors by cryptocurrency groups sorted on selected characteristics. $\Delta L(\%)$ and $\Delta H(\%)$ show the percentage difference in $R^2$ between each alternative model and IPCA for low and high quartiles, respectively. Negative values indicate IPCA outperforms the alternative model. The models are estimated on weekly returns.

```latex
\begin{tabular}{lrrrrrrrrrrrr}
\multicolumn{13}{l}{\bf Panel A: \normalfont Total $R_{tot}^2(\%)$}\\
\toprule 
& \multicolumn{2}{c}{IPCA} &       & \multicolumn{4}{c}{Instrumented observable factors}       &       & \multicolumn{4}{c}{Static PCA}  \\
\cmidrule{2-3}\cmidrule{5-8}\cmidrule{10-13}
  & \multicolumn{1}{r}{Low} & \multicolumn{1}{r}{High} &       & \multicolumn{1}{r}{Low} & \multicolumn{1}{r}{High} & $\Delta$L(\%) & $\Delta$H(\%) &       & \multicolumn{1}{r}{Low} & \multicolumn{1}{r}{High} & $\Delta$L(\%) & $\Delta$H(\%) \\
  \midrule 
{\tt capm $\beta$}  & 24.76 & 31.34 &       & 18.03 & 25.96 & -27   & -17   &       & 31.93 & 38.48 & 29    & 23 \\
{\tt size} & 24.71 & 41.03 &       & 17.30 & 40.38 & -30   & -2    &       & 32.88 & 46.84 & 33    & 14 \\
{\tt new\_add} & 30.07 & 39.52 &       & 23.98 & 36.44 & -20   & -8    &       & 41.05 & 44.92 & 37    & 14 \\
{\tt act\_add} & 26.07 & 39.90 &       & 20.24 & 36.86 & -22   & -8    &       & 37.02 & 45.47 & 42    & 14 \\
{\tt bm}    & 34.66 & 27.16 &       & 32.05 & 20.06 & -8    & -26   &       & 41.37 & 33.67 & 19    & 24 \\
          &       &       &       &       &       &       &       &       &       &       &       &  \\
{\tt \$vol} & 23.41 & 42.85 &       & 15.88 & 40.33 & -32   & -6    &       & 31.57 & 47.37 & 35    & 11 \\
{\tt bidask} & 38.55 & 24.29 &       & 34.64 & 16.19 & -10   & -33   &       & 44.76 & 31.42 & 16    & 29 \\
{\tt ivol}  & 49.61 & 22.04 &       & 46.92 & 14.26 & -5    & -35   &       & 54.42 & 30.24 & 10    & 37 \\
{\tt illiq} & 45.64 & 22.65 &       & 43.42 & 14.88 & -5    & -34   &       & 50.39 & 31.14 & 10    & 37 \\
{\tt VaR(5\%)} & 21.91 & 41.93 &       & 14.41 & 39.28 & -34   & -6    &       & 29.70 & 48.06 & 36    & 15 \\
          &       &       &       &       &       &       &       &       &       &       &       &  \\
{\tt max} $30$ & 44.47 & 23.85 &       & 41.02 & 15.99 & -8    & -33   &       & 49.89 & 32.34 & 12    & 36 \\
{\tt reddit\_act} & 25.56 & 45.68 &       & 20.32 & 43.67 & -21   & -4    &       & 32.92 & 51.24 & 29    & 12 \\
{\tt reddit\_post} & 25.97 & 42.71 &       & 20.62 & 41.12 & -21   & -4    &       & 34.15 & 48.16 & 31    & 13 \\
{\tt twitter\_f} & 27.42 & 43.10 &       & 21.06 & 39.81 & -23   & -8    &       & 35.23 & 48.44 & 28    & 12 \\
          &       &       &       &       &       &       &       &       &       &       &       &  \\
{\tt Equity capm $\beta$} & 26.67 & 29.30 &       & 20.08 & 23.42 & -25   & -20   &       & 33.60 & 36.05 & 26    & 23 \\
\midrule
          &       &       &       &       &       &       &       &       &       &       &       &  \\
\multicolumn{13}{l}{\bf Panel B: \normalfont Predictive $R_{pred}^2(\%)$}\\
\midrule 
& \multicolumn{2}{c}{IPCA} &       & \multicolumn{4}{c}{Instrumented observable factors}       &       & \multicolumn{4}{c}{Static PCA}  \\

\cmidrule{2-3}\cmidrule{5-8}\cmidrule{10-13}
  & \multicolumn{1}{r}{Low} & \multicolumn{1}{r}{High} &       & \multicolumn{1}{r}{Low} & \multicolumn{1}{r}{High} & $\Delta$L(\%) & $\Delta$H(\%) &       & \multicolumn{1}{r}{Low} & \multicolumn{1}{r}{High} & $\Delta$L(\%) & $\Delta$H(\%) \\
  \midrule 
{\tt capm $\beta$} & 2.89  & 1.79  &       & 0.87  & 0.69  & -70   & -62   &       & 0.63  & 0.50  & -78   & -72 \\
{\tt size} & 2.96  & -0.38 &       & 0.65  & 0.57  & -78   & 248   &       & 0.53  & 0.81  & -82   & 312 \\
{\tt new\_add} & 2.37  & -0.15 &       & 0.72  & 0.49  & -70   & 424   &       & 1.03  & 0.63  & -57   & 517 \\
{\tt act\_add} & 2.18  & -0.17 &       & 0.60  & 0.51  & -72   & 403   &       & 0.86  & 0.61  & -61   & 462 \\
{\tt bm}    & 0.65  & 2.61  &       & 0.71  & 0.60  & 10    & -77   &       & 0.85  & 0.53  & 32    & -80 \\
          &       &       &       &       &       &       &       &       &       &       &       &  \\
{\tt \$vol} & 3.52  & -0.35 &       & 0.80  & 0.58  & -77   & 266   &       & 0.57  & 0.71  & -84   & 302 \\
{\tt bidask} & -0.30 & 4.03  &       & 0.20  & 1.13  & 166   & -72   &       & 0.45  & 0.82  & 252   & -80 \\
{\tt ivol}  & -1.26 & 3.85  &       & -0.03 & 1.00  & 98    & -74   &       & 0.10  & 0.57  & 108   & -85 \\
{\tt illiq} & -1.06 & 3.71  &       & 0.34  & 0.89  & 132   & -76   &       & 0.57  & 0.64  & 154   & -83 \\
{\tt VaR(5\%)} & 3.67  & -1.05 &       & 0.88  & 0.16  & -76   & 116   &       & 0.40  & 0.71  & -89   & 167 \\
          &       &       &       &       &       &       &       &       &       &       &       &  \\
{\tt max} $30$ & -0.62 & 3.76  &       & 0.16  & 1.13  & 126   & -70   &       & 0.31  & 0.81  & 151   & -78 \\
{\tt reddit\_act} & 2.24  & -0.53 &       & 0.77  & 0.22  & -65   & 142   &       & 0.93  & 0.26  & -58   & 149 \\
{\tt reddit\_post} & 2.46  & -0.60 &       & 0.85  & 0.17  & -66   & 128   &       & 1.03  & 0.25  & -58   & 142 \\
{\tt twitter\_f} & 2.36  & 0.00  &       & 0.79  & 0.44  & -66   & 10705 &       & 0.73  & 0.49  & -69   & 11709 \\
          &       &       &       &       &       &       &       &       &       &       &       &  \\
{\tt Equity capm $\beta$} & 2.25  & 2.38  &       & 0.77  & 0.76  & -66   & -68   &       & 0.58  & 0.52  & -74   & -78 \\
\midrule 
 \end{tabular}
```

**[TABLE apptab6]** Model Comparison With Volatility-Scaled Returns
This table compares the in-sample $R^2_{tot}$ and $R^2_{pred}$ in percentages for models with IPCA, observable, and PCA factors. The models are estimated on daily or weekly returns scaled by the previous month’s realised volatility. For each model, it also shows the percentage change in $R^2_{tot}$ and $R^2_{pred}$ statistics relative to the unconstrained ($\Gamma_\alpha\neq0$) eight-factor IPCA model with all characteristics used as instruments. We highlight with $^*$ those performance differentials that are statistically significant at a 1% threshold level.

```latex
\begin{tabular}{lrrrrrrrrrr}
\toprule 
    &       & \multicolumn{4}{c}{Daily returns}     &       & \multicolumn{4}{c}{Weekly returns} \\
          \cmidrule{3-6}\cmidrule{8-11}
Method       & K& $R_{tot}^2$(\%)& $\Delta$(\%) & $R_{pred}^2$(\%) & $\Delta$(\%) &       & $R_{tot}^2$(\%) & $\Delta$(\%) & $R_{pred}^2$(\%) & $\Delta$(\%) \\
 \midrule
    {\tt IPCA8} (all characteristics) & 8     & 29.89 &       & 0.20  &       &       & 44.92 &       & 1.14  &  \\
     {\tt IPCA8} (all characteristics) \& $\Gamma_\alpha = 0$ & 8     & 29.87 & -0.05 & 0.19  & -5.44$^*$ &       & 44.85 & -0.16 & 1.13  & -0.73 \\
          &       &       &       &       &       &       &       &       &       &  \\
      Instrumented observable & 11    & 25.17 & -15.78$^*$ & 0.20  & 1.76  &       & 40.83 & -9.10$^*$ & 1.14  & 0.00 \\
    Instrumented observable \& $\Gamma_\alpha = 0$ & 11    & 25.03 & -16.27$^*$ & 0.07  & -67.24$^*$ &       & 40.34 & -10.20$^*$ & 0.75  & -34.34$^*$ \\
          &       &       &       &       &       &       &       &       &       &  \\
    {\tt PCA8} \& $\Gamma_\alpha = 0$ & 8     & 29.12 & -2.59$^*$ & 0.07  & -67.34$^*$ &       & 47.30 & 5.29$^*$  & 1.05  & -7.99$^*$ \\
    \midrule
    \end{tabular}
```

**[TABLE apptab7]** Model Comparison for Individual Exchanges
This table compares the $R^2_{tot}$ and $R^2_{pred}$ in percentages for models with IPCA, observable, and PCA factors. The models are estimated on daily returns for cryptocurrency pairs sampled from four major exchanges: Binance, Coinbase, Kraken, and Bitfinex. We highlight with $^*$ those performance differentials that are statistically significant at a 1% threshold level based on the testing procedure highlighted in the main text.

```latex
\begin{tabular}{lrrrrrrrrrr}
\toprule 
&       & \multicolumn{4}{c}{Binance}     &       & \multicolumn{4}{c}{Coinbase} \\
      \cmidrule{3-6}\cmidrule{8-11}
 & K& $R_{tot}^2$(\%)& $\Delta$(\%) & $R_{pred}^2$(\%) & $\Delta$(\%) &       & $R_{tot}^2$(\%) & $\Delta$(\%) & $R_{pred}^2$(\%) & $\Delta$(\%) \\
\midrule
{\tt IPCA8} (all characteristics) & 8     & 64.51 &       & 0.20  &       &       & 63.88 &       & 0.58  &  \\
 {\tt IPCA8} (all characteristics) \& $\Gamma_\alpha = 0$ & 8     & 64.49 & -0.04 & 0.16  & -17.79 &       & 63.83 & -0.08 & 0.56  & -5.08 \\
      &       &       &       &       &       &       &       &       &       &  \\
  Instrumented observable & 11    & 43.78 & -32.13$^*$ & 0.23  & 15.35$^*$  &       & 43.75 & -31.51$^*$ & 0.68  & 15.88$^*$ \\
Instrumented observable \& $\Gamma_\alpha = 0$ & 11    & 43.58 & -32.44$^*$ & 0.05$^*$  & -74.83 &       & 43.39 & -32.08$^*$ & 0.31  & -47.51$^*$ \\
      &       &       &       &       &       &       &       &       &       &  \\
{\tt PCA8} \& $\Gamma_\alpha = 0$ & 8     & 63.04 & -2.29 & 0.02  & -89.35$^*$ &       & 63.22 & -1.04 & 0.18  & -68.76$^*$ \\

\midrule
\multicolumn{11}{l}{}\\
      &       & \multicolumn{4}{c}{Kraken}     &       & \multicolumn{4}{c}{Bitfinex} \\
      \cmidrule{3-6}\cmidrule{8-11}
& K& $R_{tot}^2$(\%)& $\Delta$(\%) & $R_{pred}^2$(\%) & $\Delta$(\%) &       & $R_{tot}^2$(\%) & $\Delta$(\%) & $R_{pred}^2$(\%) & $\Delta$(\%) \\
\midrule
   {\tt IPCA8} (all characteristics) & 8     & 69.27 &       & 0.13  &       &       & 50.45 &       & 0.13  &  \\
 {\tt IPCA8} (all characteristics) \& $\Gamma_\alpha = 0$ & 8     & 69.24 & -0.05 & 0.12  & -7.11 &       & 50.40 & -0.10 & 0.05  & -63.03$^*$ \\
      &       &       &       &       &       &       &       &       &       &  \\
  Instrumented observable & 11    & 48.13 & -30.51$^*$ & 0.17  & 33.52  &       & 20.86 & -58.66$^*$ & 0.15  & 17.71 \\
Instrumented observable \& $\Gamma_\alpha = 0$ & 11    & 48.09 & -30.57$^*$ & 0.14  & 10.53 &       & 20.74 & -58.89$^*$ & 0.04  & -72.04$^*$ \\
      &       &       &       &       &       &       &       &       &       &  \\
{\tt PCA8} \& $\Gamma_\alpha = 0$ & 8     & 70.86 & 2.30 & 0.12  & -5.49 &       & 51.86 & 2.79 & 0.01  & -95.07$^*$ \\
\bottomrule
\end{tabular}
```
