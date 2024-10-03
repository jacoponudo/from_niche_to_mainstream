library(readr)
library(ggplot2)
library(dplyr)
library(pscl)

platform = 'twitter'
format = 'interaction' # interaction or thread

# This script contains: 
# - the transition from comment thread to interaction df (i.e., each row is an interaction with both the length of the interaction and the size of the thread)
# - plot of the probability of making a single comment (~alpha) relative to the number of people involved in a conversation
# - plot of the median number of comments made conditioned on having made more than one comment (lambda) relative to the number of people involved in a conversation
# - zip model to verify this relationship using the size as a predictor of alpha and lambda.

## Thread to interaction
if (platform == 'facebook') {
  data <- read_csv("~/Documents/Size_effects/DATA/sample_interactions.csv", col_types = cols(...1 = col_skip()))
} else if (platform == 'reddit') {
  data <- read_csv("~/Documents/Size_effects/RPR/reddit_size_vs_interaction.csv", col_types = cols(post_id = col_skip(), user_id = col_skip(), num_people_cat = col_skip()))
  colnames(data) = c('post_size', 'interaction_len')
  data$interaction_len=data$interaction_len+1
} else if (platform == 'usenet') {
  data <- read_csv("/home/jacoponudo/Documents/Size_effects/DATA/usenet/PRO_usenet.csv")
} else if (platform == 'twitter') {
  data <- read_csv("/home/jacoponudo/Documents/Size_effects/DATA/twitter/PRO_twitter.csv")
}

data = na.omit(data)

# Rename columns for clarity
colnames(data) = c('post_size', 'interaction_len')

data=data[data$post_size<200,]

# Create logarithmic breaks
breaks <- 10^(seq(0, ceiling(log10(max(data$post_size, na.rm = TRUE))), by = 0.1))

# Create post_size classes using logarithmic breaks
data <- data %>%
  mutate(post_size_class = cut(post_size, breaks = breaks, include.lowest = TRUE, labels = FALSE))

# Calculate the mean of alpha (interaction_len)
percentage_ones <- data %>%
  group_by(post_size_class) %>%
  summarise(percentage = mean(interaction_len == 1, na.rm = TRUE))

percentage_ones = na.omit(percentage_ones)

# Visualization
ggplot(data, aes(x = factor(post_size_class), y = interaction_len)) +
  geom_line(data = percentage_ones, aes(y = percentage), color = "orange", group = 1) +
  geom_point(data = percentage_ones, aes(y = percentage), color = "orange", size = 5) +
  scale_y_continuous(name = "Alpha", limits = c(0.2, 1)) +scale_y_continuous(name = "Log Size", limits = c(0.2, 1))
  labs(x = "Post Size Class (Log Scale)", title = "Interaction Length by Post Size Class with Percentage of 1s") +
  theme_minimal() +
  theme(axis.text.x = element_text(angle = 45, hjust = 1))


