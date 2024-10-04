library(readr)
library(ggplot2)
library(dplyr)

# List of platforms
platforms <- c('facebook', 'reddit', 'usenet', 'twitter')
data_list <- list()

# Read data for all platforms and store in a list
for (platform in platforms) {
  if (platform == 'facebook') {
    data <- read_csv("/home/jacoponudo/Documents/Size_effects/DATA/facebook/PRO_facebook.csv")
  } else if (platform == 'reddit') {
    data <- read_csv("~/Documents/Size_effects/RPR/reddit_size_vs_interaction.csv", col_types = cols(post_id = col_skip(), user_id = col_skip(), num_people_cat = col_skip()))
    colnames(data) <- c('post_size', 'interaction_len', 'month_year')
    data$interaction_len <- data$interaction_len + 1
  } else if (platform == 'usenet') {
    data <- read_csv("/home/jacoponudo/Documents/Size_effects/DATA/usenet/PRO_usenet.csv")
    colnames(data) <- c('post_size', 'interaction_len', 'month_year')
  } else if (platform == 'twitter') {
    data <- read_csv("/home/jacoponudo/Documents/Size_effects/DATA/twitter/PRO_twitter.csv")
  }
  
  # Filter data and rename columns for clarity
  #data <- data[data$post_size < 500,]
  data <- na.omit(data)
  data$platform <- platform # Add platform as a column
  data_list[[platform]] <- data
  data=na.omit(data)
}
# Combine all platform data into one data frame
combined_data <- bind_rows(data_list)

# Create uniform post size classes with a step of 5
combined_data <- combined_data %>%
  mutate(post_size_class = cut(post_size, 
                                breaks = seq(0, max(combined_data$post_size, na.rm = TRUE), by = 10), 
                                include.lowest = TRUE, 
                                right = FALSE)) # Adjusted syntax

# Calculate the mean of alpha (interaction_len) and the percentage of single comments
percentage_ones <- combined_data %>%
  group_by(platform, post_size_class) %>% 
  summarise(
    percentage = mean(interaction_len == 1, na.rm = TRUE),
    count = n(), # Count observations per class
    .groups = 'drop'
  ) %>%
  filter(count >= 1000) # Keep only classes with at least 500 observations

# Visualization
ggplot() +
  geom_line(data = percentage_ones, aes(x = post_size_class, y = percentage, color = platform, group = platform)) + # Connect points by platform
  geom_point(data = percentage_ones, aes(x = post_size_class, y = percentage, color = platform), size = 7) +
  scale_y_continuous(name = "Percentage of 1s", limits = c(0, 1)) +
  labs(x = "Post Size Class (Uniform Bins)", title = "Interaction Length by Post Size Class with Percentage of 1s Across Platforms") +
  theme_minimal() +
  theme(axis.text.x = element_text(angle = 45, hjust = 1)) +
  scale_color_manual(values = c("facebook" = "blue", "reddit" = "orange", "usenet" = "green", "twitter" = "red")) # Adjust colors as needed
