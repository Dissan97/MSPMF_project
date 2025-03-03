library(rugarch)
library(rmgarch)

get_best_dcc_garch <- function(r_rets, n_days = 5, model_type = "GJRGARCH", dist_type = "std") {
    
    if (!is.matrix(r_rets)) r_rets <- as.matrix(r_rets)
    n <- dim(r_rets)[2]
    if (n < 2) stop("Errore: DCC-GARCH richiede almeno due serie temporali.")  
    if (any(is.na(r_rets))) stop("Errore: Il dataset contiene NA.")
    
    univariate_spec <- ugarchspec(
        mean.model = list(armaOrder = c(0,0)),
        variance.model = list(model = "fGARCH", garchOrder = c(1,1), submodel = model_type),
        distribution.model = dist_type
    )

    dcc_spec <- dccspec(
        uspec = multispec(replicate(n, univariate_spec)),
        dccOrder = c(1,1),
        distribution = "mvlaplace"
    )

    # Stima del modello con gestione degli errori
    dcc_fit <- tryCatch({
        dccfit(dcc_spec, data = r_rets)
    }, error = function(e) {
        message("DCC-GARCH estimation error: ", e$message)
        return(NULL)
    })

    if (is.null(dcc_fit)) return(NULL)

    # Previsione della matrice di covarianza
    forecasts <- tryCatch({
        dccforecast(dcc_fit, n.ahead = n_days)
    }, error = function(e) {
        message("Prevision error: ", e$message)
        return(NULL)
    })

    if (is.null(forecasts)) return(NULL)

    # Output strutturato
    return(list(
        fit = dcc_fit,
        forecasts = forecasts@mforecast$H,
        correlations = rcov(dcc_fit)  
    ))
}


get_best_go_garch <- function(list_returns, f_horizon) {
    
}

get_best_cdcc_garch <- function(r_rets, n_days = 5, model_type = "GJRGARCH", dist_type = "sstd") {
    
    # Controllo sugli input
    if (!is.matrix(r_rets)) r_rets <- as.matrix(r_rets)
    n <- dim(r_rets)[2]
    if (n < 2) stop("Errore: cDCC-GARCH richiede almeno due serie temporali.")  
    if (any(is.na(r_rets))) stop("Errore: Il dataset contiene NA.")
    
    message("🟢 Input data check: OK")
    
    # Specifica GARCH univariato flessibile
    univariate_spec <- ugarchspec(
        mean.model = list(armaOrder = c(0,0)),
        variance.model = list(model = "fGARCH", garchOrder = c(1,1), submodel = model_type),
        distribution.model = dist_type
    )

    # Specifica cDCC-GARCH flessibile
    cdcc_spec <- dccspec(
        uspec = multispec(replicate(n, univariate_spec)),
        dccOrder = c(1,1),
        lag.criterion = "AIC",
        robust.control = list("gamma" = 0.25, "delta" = 0.01, "nc" = 10, "ns" = 500),
        model = "aDCC",
        distribution = "mvlaplace"
    )

    message("🟢 DCC specification: OK")

    # Stima del modello con gestione errori
    cdcc_fit <- tryCatch({
        fit <- dccfit(cdcc_spec, data = r_rets)
        message("🟢 Model fitting: OK")
        return(fit)
    }, error = function(e) {
        message("❌ Errore nella stima del cDCC-GARCH: ", e$message)
        return(NULL)
    })

    if (is.null(cdcc_fit)) return(NULL)

    # Previsione della matrice di covarianza
    forecasts <- tryCatch({
        forecast <- dccforecast(cdcc_fit, n.ahead = n_days)
        message("🟢 Forecasting: OK")
        return(forecast)
    }, error = function(e) {
        message("❌ Errore nella previsione cDCC-GARCH: ", e$message)
        return(NULL)
    })

    if (is.null(forecasts)) return(NULL)

    # Output strutturato
    return(list(
        fit = cdcc_fit,
        forecasts = forecasts@mforecast$H,
        correlations = rcov(cdcc_fit)
    ))
}
