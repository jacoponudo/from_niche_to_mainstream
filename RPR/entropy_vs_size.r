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
  #data <- data[data$post_size < 5000,]
  data <- na.omit(data)
  data$platform <- platform # Add platform as a column
  data_list[[platform]] <- data
}

combined_data <- combined_data %>%
  filter(platform == 'facebook' & grepl('2011', month_year))
# Combine all platform data into one data frame
combined_data <- bind_rows(data_list)
combined_data$interaction_len <- cut(combined_data$interaction_len, breaks = c(0, 1:10, Inf), labels = c(as.character(1:10), "10-nf"), right = FALSE)

# Create uniform post size classes with a step of 10
combined_data <- combined_data %>%
  mutate(post_size_class = cut(log(post_size + 1),  # Adding 1 to avoid log(0)
                                breaks = seq(0, log(max(combined_data$post_size, na.rm = TRUE) + 1), length.out = 50), 
                                include.lowest = TRUE, 
                                right = FALSE))

# Calculate the entropy of interaction_len for each post size class
entropy_data <- combined_data %>%
  group_by(platform, post_size_class) %>%
  summarise(
    entropy = -sum((table(interaction_len) / n()) * log(table(interaction_len) / n()), na.rm = TRUE),
    count = n(), # Count observations per class
    .groups = 'drop'
  ) %>%
  filter(count >= 5000) # Keep only classes with at least 1000 observations

# Visualization
ggplot() +
  geom_line(data = entropy_data, aes(x = post_size_class, y = entropy, color = platform, group = platform)) + # Connect points by platform
  geom_point(data = entropy_data, aes(x = post_size_class, y = entropy, color = platform), size = 7) +
  scale_y_continuous(name = "Entropy", limits = c(0, max(entropy_data$entropy, na.rm = TRUE))) +
  labs(x = "Post Size Class (Uniform Bins)", title = "Entropy of Interaction Length by Post Size Class Across Platforms") +
  theme_minimal() +
  theme(axis.text.x = element_text(angle = 45, hjust = 1)) +
  scale_color_manual(values = c("facebook" = "blue", "reddit" = "orange", "usenet" = "green", "twitter" = "red")) # Adjust colors as needed

