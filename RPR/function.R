# Definisci una funzione per calcolare la probabilità di avere meno di 3 commenti
calc_prob <- function(size_label, coef_zip) {
  # Calcola lambda per la parte di conteggio
  lambda <- exp(coef_zip["count_(Intercept)"] +
                  coef_zip[paste0("count_num_people_cat", size_label)])
  
  # Calcola la probabilità di zero
  p_zero <- exp(coef_zip["zero_(Intercept)"] +
                  coef_zip[paste0("zero_num_people_cat", size_label)]) / 
    (1 + exp(coef_zip["zero_(Intercept)"] +
               coef_zip[paste0("zero_num_people_cat", size_label)]))
  
  # Probabilità di avere meno di 3 commenti
  p_less_than_3 <- ppois(2, lambda) * (1 - p_zero) + p_zero
  return(p_less_than_3)
}
