library(rugarch)
library(rmgarch)

dcc_garch_fit <- function(r_rets, n_days = 5, model_type = "GARCH", dist_type = "ged") {
    
    if (!is.matrix(r_rets)) r_rets <- as.matrix(r_rets)
    n <- dim(r_rets)[2]
    if (n < 2) stop("Errore: DCC-GARCH at least 2 timeseries.")  
    if (any(is.na(r_rets))) stop("Errore: Il dataset has NA.")
    
    univariate_spec <- ugarchspec(
        mean.model = list(armaOrder = c(3,3)),
        variance.model = list(model = "fGARCH", garchOrder = c(1,1), submodel = model_type),
        distribution.model = dist_type
    )

    dcc_spec <- dccspec(
        uspec = multispec(replicate(n, univariate_spec)),
        dccOrder = c(1, 1),
        distribution = "mvlaplace",
        lag.max = 10
    )

    
    dcc_fit <- tryCatch({
        dccfit(dcc_spec, data = r_rets)
    }, error = function(e) {
        message("DCC-GARCH estimation error: ", e$message)
        return(NULL)
    })

    if (is.null(dcc_fit)) return(NULL)
    
    forecasts <- tryCatch({
        dccforecast(dcc_fit, n.ahead = n_days)
    }, error = function(e) {
        message("Prevision error: ", e$message)
        return(NULL)
    })
    residuals_matrix <- residuals(dcc_fit)
    
    

    if (is.null(forecasts)) return(NULL)
    #show(dccforecast(dcc_fit, n.ahead = n_days))
    write.csv(residuals_matrix, "./temp/residual_matrix.csv")
    write.csv(rcov(dcc_fit), "./temp/rcov.csv")
    write.csv(rcor(dcc_fit), "./temp/rcor.csv")
    write.csv(rskew(dcc_fit), "./temp/rskew.csv")
    write.csv(sigma(dcc_fit), "./temp/sigma.csv")
    write.csv(coef(dcc_fit), "./temp/coef.csv")
    write.csv(residuals_matrix / sigma(dcc_fit), "./temp/std_residuals.csv")
    write.csv(sigma(forecasts), "./temp/forecast_sigma.csv")
    write.csv(fitted(forecasts), "./temp/forecast_fitted.csv")
    
    # Output strutturato
    return(list(
        fit = dcc_fit,
        forecasts = forecasts@mforecast$H,
        correlations = rcov(dcc_fit),
        residuals =as.matrix(residuals_matrix)
    ))
}


go_garch_fit <- function(r_rets, n_days = 5, model_type = "GARCH", dist_type = "ged") {

    univariate_spec <- ugarchspec(
        mean.model = list(armaOrder = c(3,3)),
        variance.model = list(model = "fGARCH", garchOrder = c(1,1), submodel = model_type),
        distribution.model = dist_type
    )
    
    spec = gogarchspec(mean.model = list(demean = "constant"),
    variance.model = list(model = "fGARCH", garchOrder = c(1,1), submodel = model_type),
    distribution.model =  "manig",ica = "fastica")
    fit = gogarchfit(spec = spec, data = r_rets, gfun = "tanh")
    # The likelihood of the model
    

    show(likelihood(fit))
    show(fit)
    write.csv(residuals(fit) / sigma(fit), "./temp/std_residuals.csv")
}