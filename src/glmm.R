# install.packages("lme4", repos="http://cran.us.r-project.org")
# install.packages("dplyr", repos="http://cran.us.r-project.org")
# install.packages("broom.mixed", repos="http://cran.us.r-project.org")
# install.packages("tidyverse", repos="http://cran.us.r-project.org")
# install.packages("glmmTMB", repos="http://cran.us.r-project.org")

library(lme4)
library(dplyr)
library(broom)
library(broom.mixed)
library(glmmTMB)

fixed_effect_levels <- list(
    age = c("18-24 years old", "25-34 years old", "35-44 years old", "45-54 years old", "55-64 years old", "65+ years old"),
    gender = c("Male", "Female", "Non-binary / third gender", 'Prefer not to say'),
    ethnicity = c('White', 'Prefer not to say', 'Black', 'Hispanic', 'Mixed', 'Asian', 'Other'),
    chosen_model = c('luminous-supreme-control','command-light','command-nightly','HuggingFaceH4/zephyr-7b-beta','claude-2.1','models/chat-bison-001','mistralai/Mistral-7B-Instruct-v0.1','meta-llama/Llama-2-7b-chat-hf','timdettmers/guanaco-33b-merged','command','gpt-4','tiiuae/falcon-7b-instruct','gpt-3.5-turbo','meta-llama/Llama-2-70b-chat-hf','gpt-4-1106-preview','claude-instant-1','claude-2','OpenAssistant/oasst-sft-4-pythia-12b-epoch-3.5','meta-llama/Llama-2-13b-chat-hf','google/flan-t5-xxl','luminous-extended-control'),
    conversation_type = c('unguided', 'controversy guided', 'values guided'),
    education = c("University Bachelors Degree", "Some Secondary", "Some University but no degree", "Vocational", "Completed Secondary School", "Graduate / Professional degree", "Completed Primary School", "Prefer not to say", "Some Primary"),
    birth_region = c("Europe", "Americas", "Africa", "Asia", "Oceania", "Prefer not to say"),
    reside_region = c("Europe", "Americas", "Africa", "Asia", "Oceania", "Prefer not to say"),
    religion = c("No Affiliation", "Christian", "Jewish", "Muslim", "Other", "Prefer not to say"),
    employment_status = c('Working full-time', 'Working part-time', 'Student', 'Homemaker / Stay-at-home parent', 'Unemployed, seeking work', 'Unemployed, not seeking work', 'Retired', 'Prefer not to say')
   )

process_df <- function(df){
  for (fixed_effect in names(fixed_effect_levels)){
    if (fixed_effect %in% names(df)){
      df[[fixed_effect]] = factor(df[[fixed_effect]], level = fixed_effect_levels[[fixed_effect]])
    }
  }
  return(df)
}

check_converge <- function(model, fit){
  sc_grad <- model$sdr$par.fixed
  max_sc_grad <- max(abs(sc_grad))
    
  fit$converged <- model$fit$convergence == 0
  fit$convergence_message <- model$fit$message
  fit$pd_hessian <- model$sdr$pdHess
  fit$grad_converged <- max_sc_grad < 0.002
  fit$max_grad <- max_sc_grad
  return(fit)
}

# Function to read CSV and run mixed effects regression
run_mixed_effects_regression <- function(df_fpath, response_variable, fixed_factors, random_factors, outdir) {
  # Load df
  df <- read.csv(df_fpath)

  # Convert categorical variables to factors
  df = process_df(df)

  model_formula = as.formula(paste(response_variable, "~", fixed_factors, "+", random_factors))
  
  if (max(df[[response_variable]]) <= 1.01){
    n = 10000
    df[[response_variable]] = (df[[response_variable]]*(n-1) + 0.5)/n

    model = glmmTMB(model_formula,
                  data = df, 
                  family=beta_family(),
                  REML=TRUE,
                  control=glmmTMBControl(
                      parallel = list(nthreads = parallel::detectCores() - 1),
                      optCtrl = list(iter.max = 10000, eval.max = 10000)
                  )
                )  
    param_name = "beta_"
  }
  else {
    filtered_data <- df
    filtered_data[[response_variable]] <- filtered_data[[response_variable]] / 1000  # Convert to thousands
    model = glmmTMB(model_formula,
                  data = filtered_data, 
                  family = gaussian(link = "identity"),
                  REML=TRUE,
                  control=glmmTMBControl(
                      parallel = list(nthreads = parallel::detectCores() - 1),
                      optCtrl = list(iter.max = 10000, eval.max = 10000)
                  )
                )  
    param_name = "beta_"
  }

  estimates = tidy(model)
  for (confidence_level in c(0.95, 0.99)){
    estimates = merge(estimates, confint(model, method = "Wald", parm = param_name, level=confidence_level), by.x="term", by.y=0, all=TRUE)
  }

  fit = glance(model)
  fit = check_converge(model, fit)

  write.csv(estimates, paste(outdir, "estimates.csv", sep="/"), row.names = FALSE)
  write.csv(fit, paste(outdir, "fit.csv", sep="/"), row.names= FALSE) 
}


args <- commandArgs(trailingOnly = TRUE)
Sys.setenv(MKL_NUM_THREADS = "1")
run_mixed_effects_regression(args[1], args[2], args[3], args[4], args[5])
