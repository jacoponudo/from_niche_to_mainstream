# Import

data=reddit_sizepost_vs_sizeinteraction
colnames(data)
install.packages("pscl")
library(pscl)


# Modello ZIP con size continua

zip_model <- zeroinfl(num_comments_minus_1 ~ num_people | num_people, data = data, dist = "poisson")
summary(zip_model)


# Modello ZIP con size categorica

data$num_people_cat <- cut(data$num_people, breaks = c(-Inf, 50, 100,150,200, Inf), labels = c("0-50", "51-100","101-150", "151-200","200+"))
zip_model <- zeroinfl(num_comments_minus_1 ~ num_people_cat | num_people_cat, data = data, dist = "poisson")
summary(zip_model)


# Calcola la probabilità di osservare un'interazione più corta di 3 commenti per size = 30 e size = 250

coef_zip <- coef(zip_model)
size_values <- c(0, 1)
probabilities <- sapply(size_values, function(size) {
  lambda <- exp(coef_zip["count_(Intercept)"] + coef_zip["count_num_people_cat200+"] *size)
  p_zero <- exp(coef_zip["zero_(Intercept)"] + coef_zip["zero_num_people_cat200+"]*size) / (1 + exp(coef_zip["zero_(Intercept)"] + coef_zip["zero_num_people_cat200+"]*size) )
  p_less_than_3 <- ppois(1, lambda) * (1 - p_zero) + p_zero
  return(p_less_than_3)
})
names(probabilities) <- size_values
probabilities
