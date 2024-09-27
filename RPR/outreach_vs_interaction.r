library(readr)
data <- read_csv("Documents/Size_effects/DATA/interacions/facebook_outreach_vs_interaction.csv", 
                                             col_types = cols(...1 = col_skip(), post_id = col_skip(), 
                                                              alpha = col_skip()))
data=na.omit(data)
colnames(data)=c("interaction_len","post_size")
platform='facebook'
library(dplyr)

# Calculate quantiles outside of mutate
quantiles <- quantile(data$post_size, probs = seq(0, 1, length.out = 41), na.rm = TRUE)

# Create the post_size_class within mutate
reddit_size_vs_interaction <- data %>%
  mutate(
    interaction = interaction_len,
    post_size_class = cut(
      post_size,
      breaks = unique(quantiles),
      include.lowest = TRUE,
      labels = paste0(
        "(", 
        round(unique(quantiles)[-length(unique(quantiles))], 2), 
        ", ", 
        round(unique(quantiles)[-1], 2), 
        "]"
      )
    )
  )

percentage_ones <- reddit_size_vs_interaction %>%
  group_by(post_size_class) %>%
  summarise(percentage = mean(interaction == 1))

# Plot Alpha vs Size
alpha_plot <- ggplot(reddit_size_vs_interaction, aes(x = post_size_class, y = interaction)) +
  geom_line(data = percentage_ones, aes(y = percentage), color = "orange", group = 1) +
  geom_point(data = percentage_ones, aes(y = percentage), color = "orange", size = 2) +
  scale_y_continuous(name = "Alpha", limits = c(0.5, 1)) +
  labs(x = "Post Size Class", title = paste("Alpha vs Size on", platform)) +
  theme_minimal() +
  theme(axis.text.x = element_text(angle = 45, hjust = 1))

ggsave(paste0(platform, "_alpha_vs_size.png"), plot = alpha_plot, width = 8, height = 6)

# Plot Lambda vs Size
reddit_size_vs_interaction <- data %>%
  mutate(interaction = interaction_len) %>%
  filter(interaction > 1) %>%
  mutate(
    post_size_class = cut(
      post_size,
      breaks = quantile(post_size, probs = seq(0, 1, length.out = 41), na.rm = TRUE),
      include.lowest = TRUE,
      labels = paste0(
        "(", 
        round(quantile(post_size, probs = seq(0, 1, length.out = 41), na.rm = TRUE)[-length(quantile(post_size, probs = seq(0, 1, length.out = 21), na.rm = TRUE))], 2), 
        ", ", 
        round(quantile(post_size, probs = seq(0, 1, length.out = 41), na.rm = TRUE)[-1], 2), 
        "]"
      )
    )
  )

mean_interactions <- reddit_size_vs_interaction %>%
  group_by(post_size_class) %>%
  summarise(mean_interaction = mean(interaction, na.rm = TRUE))

lambda_plot <- ggplot(mean_interactions, aes(x = post_size_class, y = mean_interaction)) +
  geom_line(color = "blue", group = 1) +
  geom_point(color = "blue", size = 2) +
  labs(x = "Post Size Class", y = "Lambda", title = paste("Lambda vs Size on", platform)) +
  scale_y_continuous(name = "Lambda", limits = c( 1,10)) +
  theme_minimal() +
  theme(axis.text.x = element_text(angle = 45, hjust = 1))

ggsave(paste0(platform, "_lambda_vs_size.png"), plot = lambda_plot, width = 8, height = 6)


## ZIP 
if(platform=='facebook'){
  data <- data[sample(nrow(data), nrow(data)/1000), ]
}
data$interaction_len_minus_1=data$interaction_len-1
data$post_size_cat <- cut(data$post_size, breaks = c(-Inf, 50, 100,150, Inf), labels = c("0-50", "51-100","101-150","150+"))

zip_model <- zeroinfl(interaction_len_minus_1 ~ post_size | post_size, data = data, dist = "poisson")
summary(zip_model)

zip_model <- zeroinfl(interaction_len_minus_1 ~ post_size_cat | post_size_cat, data = data, dist = "poisson")
summary(zip_model)
coef_zip <- coef(zip_model)
size_values <- c(0, 1)
probabilities <- sapply(size_values, function(size) {
  lambda <- exp(coef_zip["count_(Intercept)"] + coef_zip["count_post_size_cat150+"] *size)
  p_zero <- exp(coef_zip["zero_(Intercept)"] + coef_zip["zero_post_size_cat150+"]*size) / (1 + exp(coef_zip["zero_(Intercept)"] + coef_zip["zero_post_size_cat150+"]*size) )
  p_less_than_3 <- ppois(1, lambda) * (1 - p_zero) + p_zero
  return(p_less_than_3)})

names(probabilities) <- size_values
probabilities

