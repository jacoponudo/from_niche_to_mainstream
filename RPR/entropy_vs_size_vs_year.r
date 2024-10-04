library(readr)
library(ggplot2)
library(dplyr)

# Read Facebook data only
facebook_data <- read_csv("/home/jacoponudo/Documents/Size_effects/DATA/facebook/PRO_facebook.csv")

# Filter data and rename columns for clarity
facebook_data <- facebook_data[facebook_data$post_size < 1000,]
facebook_data <- na.omit(facebook_data)

# Assuming the 'month_year' column is in a date format, convert it to Date type
facebook_data$month_year <- as.Date(paste0(facebook_data$month_year, "-01"), format="%Y-%m-%d")

# Extract year from month_year
facebook_data$year <- format(facebook_data$month_year, "%Y")
combined_data$interaction_len <- cut(combined_data$interaction_len, breaks = c(-Inf, 1, 3, 8, 10, 20, Inf), labels = c("1", "2-3", "4-8", "8-10", "10-20", "20-nf"), right = TRUE)

# Create uniform post size classes with a step of 10
facebook_data <- facebook_data %>%
  mutate(post_size_class = cut(post_size, 
                                breaks = seq(0, max(facebook_data$post_size, na.rm = TRUE), by = 20), 
                                include.lowest = TRUE, 
                                right = FALSE)) # Adjusted syntax

# Calculate the entropy of interaction_len for each post size class
entropy_data_facebook <- facebook_data %>%
  group_by(year, post_size_class) %>%
  summarise(
    entropy = -sum((table(interaction_len) / n()) * log(table(interaction_len) / n()), na.rm = TRUE),
    count = n(), # Count observations per class
    .groups = 'drop'
  ) %>%
  filter(count >= 1000) # Keep only classes with at least 1000 observations

# Visualization for Facebook
ggplot() +
  geom_line(data = entropy_data_facebook, aes(x = post_size_class, y = entropy, group = year, color = year)) + 
  geom_point(data = entropy_data_facebook, aes(x = post_size_class, y = entropy, group = year, color = year), size = 3) +
  scale_y_continuous(name = "Entropy", limits = c(0, max(entropy_data_facebook$entropy, na.rm = TRUE))) +
  labs(x = "Post Size Class (Uniform Bins)", title = "Entropy of Interaction Length by Post Size Class for Facebook") +
  theme_minimal() +
  theme(axis.text.x = element_text(angle = 45, hjust = 1)) +
  scale_color_discrete(name = "Year") # Automatically generates colors for each year
