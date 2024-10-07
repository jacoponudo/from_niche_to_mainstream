library(readr)
library(ggplot2)
library(dplyr)

# List of platforms including Voat
platforms <- c('facebook', 'reddit', 'usenet', 'twitter', 'voat')
data_list <- list()

# Read data for all platforms and store in a list
for (platform in platforms) {
  if (platform == 'facebook') {
    data <- read_csv("/home/jacoponudo/Documents/Size_effects/DATA/facebook/PRO_facebook.csv")
  } else if (platform == 'reddit') {
    data <- read_csv("/home/jacoponudo/Documents/Size_effects/DATA/reddit/PRO_reddit.csv")
  } else if (platform == 'usenet') {
    data <- read_csv("/home/jacoponudo/Documents/Size_effects/DATA/usenet/PRO_usenet.csv")
    colnames(data) <- c('post_size', 'interaction_len', 'month_year')
  } else if (platform == 'twitter') {
    data <- read_csv("/home/jacoponudo/Documents/Size_effects/DATA/twitter/PRO_twitter.csv")
  } else if (platform == 'voat') {
    data <- read_csv("/home/jacoponudo/Documents/Size_effects/DATA/voat/PRO_voat.csv")
  } 
  
  # Filter and clean data
  data <- na.omit(data)
  data$platform <- platform # Add platform as a column
  data_list[[platform]] <- data
}

# Combine all platform data into one data frame
combined_data <- bind_rows(data_list)

# Uniformly bin interaction lengths
combined_data$interaction_len <- cut(combined_data$interaction_len, 
                                      breaks = c(0, 1:30, Inf), 
                                      labels = c(as.character(1:30), "30-nf"), 
                                      right = FALSE)

# Create uniform post size classes
combined_data <- combined_data %>%
  mutate(post_size_class = cut(log(post_size + 1),  
                                breaks = seq(0, log(max(combined_data$post_size, na.rm = TRUE) + 1), length.out = 50), 
                                include.lowest = TRUE, 
                                right = FALSE))

# Calculate the entropy of interaction_len for each post size class
entropy_data <- combined_data %>%
  group_by(platform, post_size_class) %>%
  summarise(
    entropy = -sum((table(interaction_len) / n()) * log(table(interaction_len) / n()), na.rm = TRUE),
    count = n(), 
    .groups = 'drop'
  ) %>%
  filter(count >= 1000) # Keep only classes with sufficient observations

# Visualization
ggplot() +
  geom_line(data = entropy_data, aes(x = post_size_class, y = entropy, color = platform, group = platform)) +
  geom_point(data = entropy_data, aes(x = post_size_class, y = entropy, color = platform), size = 7) +
  scale_y_continuous(name = "Entropy", limits = c(0, max(entropy_data$entropy, na.rm = TRUE))) +
  labs(x = "Post Size Class (Uniform Bins)", title = "Entropy of Interaction Length by Post Size Class Across Platforms") +
  theme_minimal() +
  theme(axis.text.x = element_text(angle = 45, hjust = 1)) +
  scale_color_manual(values = c("facebook" = "blue", "reddit" = "orange", "usenet" = "green", "twitter" = "red", "voat" = "purple")) # Added color for Voat


