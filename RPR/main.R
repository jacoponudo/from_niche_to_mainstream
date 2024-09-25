library(readr)
library(ggplot2)
library(dplyr)
library(readr)
library(pscl)
data <- read_csv("reddit_size_vs_interaction.csv")
format='interaction' # interaction or thread

# Questo script contiene: 
# - il passaggio dal thread di commenti a interaction df (ovvero ogni riga è un interazione e contene sia la len dell'intrazione che la size del thread)
# - plot della probabilità do fare un solo commento (~alpha) rispetto al numero di persone coinvolte in una conversazione
# - plot del numero mediano di commenti che si fanno condizionata rispetto ad aver fatto piu di un commento (lambda) rispetto al numero di persone coinvolte in una conversazione
# - modello zip per verificare questa relazione usando la size come predittore di alpha e lambda.

##  Tread to interaction
if(format=='thread'){
  if(min(data$num_comments_minus_1)==0){
    data$num_comments_minus_1=data$num_comments_minus_1+1}
}else{
  if(min(data$num_comments_minus_1)==0){
    data$num_comments_minus_1=data$num_comments_minus_1+1}
  data <- data %>%rename(post_size = num_people,interaction_len = num_comments_minus_1)}


## Alpha vs Size
reddit_size_vs_interaction <- data %>% mutate(interaction = interaction_len, post_size_class = cut(post_size, breaks = quantile(post_size, probs = seq(0, 1, length.out = 41), na.rm = TRUE), include.lowest = TRUE, labels = paste0("(", round(quantile(post_size, probs = seq(0, 1, length.out = 41), na.rm = TRUE)[-length(breaks)], 2), ", ", round(quantile(post_size, probs = seq(0, 1, length.out = 41), na.rm = TRUE)[-1], 2), "]")))
percentage_ones <- reddit_size_vs_interaction %>% group_by(post_size_class) %>% summarise(percentage = mean(interaction == 1) )
ggplot(reddit_size_vs_interaction, aes(x = post_size_class, y = interaction)) +geom_line(data = percentage_ones, aes(y = percentage), color = "orange", group = 1) +geom_point(data = percentage_ones, aes(y = percentage), color = "orange", size = 2) +scale_y_continuous(name = "Alpha") +labs(x = "Post Size Class", title = "Interaction Length by Post Size Class with Percentage of 1s") +theme_minimal() +theme(axis.text.x = element_text(angle = 45, hjust = 1))


## Lambda vs Size
reddit_size_vs_interaction <- data %>%mutate(interaction = interaction_len ) %>%filter(interaction > 1) %>%mutate(post_size_class = cut(post_size, breaks = quantile(post_size, probs = seq(0, 1, length.out = 41), na.rm = TRUE), include.lowest = TRUE, labels = paste0("(", round(quantile(post_size, probs = seq(0, 1, length.out = 41), na.rm = TRUE)[-length(breaks)], 2), ", ", round(quantile(post_size, probs = seq(0, 1, length.out = 41), na.rm = TRUE)[-1], 2), "]"))) 
mean_interactions <- reddit_size_vs_interaction %>% group_by(post_size_class) %>% summarise(mean_interaction = mean(interaction, na.rm = TRUE))
ggplot(mean_interactions, aes(x = post_size_class, y = mean_interaction)) +geom_line(color = "blue", group = 1) + geom_point(color = "blue", size = 2) + labs(x = "Post Size Class", y = "Lambda", title = "Mean Interaction by Post Size Class") + theme_minimal() + theme(axis.text.x = element_text(angle = 45, hjust = 1))


## ZIP 
data$interaction_len_minus_1=data$interaction_len-1
data$post_size_cat <- cut(data$post_size, breaks = c(-Inf, 50, 100,150, Inf), labels = c("0-50", "51-100","101-150","150+"))

zip_model <- zeroinfl(interaction_len_minus_1 ~ post_size | post_size, data = data, dist = "poisson")
summary(zip_model)

zip_model <- zeroinfl(interaction_len_minus_1 ~ post_size_cat | post_size_cat, data = data, dist = "poisson")
summary(zip_model)
coef_zip <- coef(zip_model)
size_values <- c(0, 1)
probabilities <- sapply(size_values, function(size) {
  lambda <- exp(coef_zip["count_(Intercept)"] + coef_zip["count_post_size_cat200+"] *size)
  p_zero <- exp(coef_zip["zero_(Intercept)"] + coef_zip["zero_post_size_cat200+"]*size) / (1 + exp(coef_zip["zero_(Intercept)"] + coef_zip["zero_num_people_cat200+"]*size) )
  p_less_than_3 <- ppois(1, lambda) * (1 - p_zero) + p_zero
  return(p_less_than_3)})

names(probabilities) <- size_values
probabilities



