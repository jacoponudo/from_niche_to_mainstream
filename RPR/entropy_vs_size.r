library(readr)
library(ggplot2)
library(dplyr)

# List of platforms including Gab
platforms <- c('facebook', 'reddit', 'usenet', 'twitter', 'voat', 'gab')
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
  } else if (platform == 'gab') {
    data <- read_csv("/home/jacoponudo/Documents/Size_effects/DATA/gab/PRO_gab.csv")
    # Adjust column names as necessary for Gab data
    colnames(data) <- c('post_size', 'interaction_len', 'month_year')
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

# Create the plot
plot <- ggplot() +
  geom_line(data = entropy_data, aes(x = post_size_class, y = entropy, color = platform, group = platform)) +
  geom_point(data = entropy_data, aes(x = post_size_class, y = entropy, color = platform), size = 1.5) +
  geom_vline(xintercept = 18, linetype = "dashed", color = "black") +
  scale_y_continuous(name = "Entropy", limits = c(0, max(entropy_data$entropy, na.rm = TRUE))) +
  labs(x = "Post Size Class (Uniform Bins)", title = "Entropy of Interaction Length by Post Size Class Across Platforms") +
  theme_minimal() +
  theme(axis.text.x = element_text(angle = 45, hjust = 1, size = 14),
        axis.text.y = element_text(size = 14),
        axis.title.x = element_text(size = 16),
        axis.title.y = element_text(size = 16),
        plot.title = element_text(size = 18, hjust = 0.5)) +
  scale_color_manual(values = c("facebook" = "blue", "reddit" = "orange", "usenet" = "green", "twitter" = "red", "voat" = "purple", "gab" = "brown"))

# Save the plot with 16:8 aspect ratio
ggsave("/home/jacoponudo/Documents/Size_effects/PLT/4_size_entropy/entropy_plot.png", plot = plot, width = 16, height = 8, dpi = 300)
