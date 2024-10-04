library(readr)
library(ggplot2)
library(dplyr)
library(pscl)

platform = 'facebook'

# This script contains: 
# - the transition from comment thread to interaction df (i.e., each row is an interaction with both the length of the interaction and the size of the thread)
# - plot of the probability of making a single comment (~alpha) relative to the number of people involved in a conversation
# - plot of the median number of comments made conditioned on having made more than one comment (lambda) relative to the number of people involved in a conversation
# - zip model to verify this relationship using the size as a predictor of alpha and lambda.

## Thread to interaction
if (platform == 'facebook') {
  data <- read_csv("/home/jacoponudo/Documents/Size_effects/DATA/facebook/PRO_facebook.csv")
} else if (platform == 'reddit') {
  data <- read_csv("~/Documents/Size_effects/RPR/reddit_size_vs_interaction.csv", col_types = cols(post_id = col_skip(), user_id = col_skip(), num_people_cat = col_skip()))
  colnames(data) = c('post_size', 'interaction_len')
  data$interaction_len = data$interaction_len + 1
} else if (platform == 'usenet') {
  data <- read_csv("/home/jacoponudo/Documents/Size_effects/DATA/usenet/PRO_usenet.csv")
} else if (platform == 'twitter') {
  data <- read_csv("/home/jacoponudo/Documents/Size_effects/DATA/twitter/PRO_twitter.csv")
}

data = na.omit(data)

# Usa 'month_year' anziché 'year'
data$month_year <- as.factor(data$month_year)

# Funzione per calcolare l'entropia
calculate_entropy <- function(x) {
  freq <- prop.table(table(x))
  -sum(freq * log(freq), na.rm = TRUE)
}

# Raggruppa per 'month_year' e calcola sia l'entropia di 'interaction_len' che la media di 'post_size'
summary_per_month <- data %>%
  group_by(month_year) %>%
  summarise(
    entropy = calculate_entropy(interaction_len),
    avg_post_size = mean(post_size, na.rm = TRUE)
  )

# Visualizza il risultato
print(summary_per_month)






plot(summary_per_month$entropy,log(summary_per_month$avg_post_size))




# Load necessary library
library(ggplot2)

# Ensure the month_year column is in Date format
summary_per_month$month_year <- as.Date(paste0(summary_per_month$month_year, "-01"), format = "%Y-%m-%d")

# Create the time series plot
ggplot(summary_per_month, aes(x = month_year, y = entropy)) +
  geom_line(color = "blue") +  # Line plot for entropy
  geom_point(color = "red") +   # Points for each data point
  labs(title = "Time Series of Entropy", 
       x = "Month and Year", 
       y = "Entropy") +
  theme_minimal() +              # Use a minimal theme
  theme(axis.text.x = element_text(angle = 45, hjust = 1))  # Rotate x-axis labels for better readability
