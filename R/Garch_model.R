library(rugarch)

get_garch_best_models <- function(returns, f_horizon) {
    distributions <- c("std", "ged", "snorm", "sstd")
    
    best_shibata <- -Inf
    ml <- -Inf
    best_model <- NULL
    best_p <- 0
    best_q <- 0
    best_dist <- ""

    for (dist in distributions) {
        spec <- spec <- ugarchspec(
            variance.model = list(model = "fGARCH", garchOrder = c(1,1), submodel = "GJRGARCH"),
            mean.model = list(armaOrder = c(1,1)),  
            distribution.model = dist,
            start.pars = list(omega = 0.01, alpha1 = 0.05, beta1 = 0.9, gamma1 = 0.01)  
        )
        fit <- tryCatch(
            ugarchfit(spec, returns, solver.control = list(maxeval = 20000)),
            error = function(e) NULL 
        )
        
        if (is.null(fit) || fit@fit$convergence != 0) {
            next
        }

        
        criteria <- tryCatch(infocriteria(fit), error = function(e) NULL)
        if (is.null(criteria)) {
            next
        }

        shibata <- criteria[3]  
        lh <- likelihood(fit)

        if (ml < lh) {
            ml <- lh
            best_shibata <- shibata
            best_dist <- dist
            best_model <- fit
        }
    }

    if (is.null(best_model)) {
        stop("Nessun modello valido trovato. Verifica i dati di input.")
    }

    # Ottenere le previsioni
    forecast_garch <- ugarchforecast(best_model, n.ahead = f_horizon, method="bootstrap")
    params <- coef(best_model)
    #show(sigma(best_model))
    return (list(
        "distribution" = best_dist,
        "shibata" = best_shibata,
        "conditional_volatility" = sigma(best_model),
        "garch_residuals" = residuals(best_model),
        "volatility_forecast" = sigma(forecast_garch),
        "conditional_mean" = fitted(forecast_garch),
        "omega" = if ("omega" %in% names(params)) params["omega"] else NA,
        "alpha1" = if ("alpha1" %in% names(params)) params["alpha1"] else NA,
        "beta1" = if ("beta1" %in% names(params)) params["beta1"] else NA
    ))
}
