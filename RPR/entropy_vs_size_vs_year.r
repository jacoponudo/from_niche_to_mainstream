library(readr)
library(ggplot2)
library(dplyr)

# Define the platform you want to analyze
selected_platform <- 'usenet'

# Dictionary to map the platform to the appropriate file path
platform_paths <- list(
  'facebook' = "/home/jacoponudo/Documents/Size_effects/DATA/facebook/PRO_facebook.csv",
  'reddit' = "~/Documents/Size_effects/RPR/reddit_size_vs_interaction.csv",
  'usenet' = "/home/jacoponudo/Documents/Size_effects/DATA/usenet/PRO_usenet.csv",
  'twitter' = "/home/jacoponudo/Documents/Size_effects/DATA/twitter/PRO_twitter.csv"
)

# Read data for the selected platform
if (selected_platform == 'facebook') {
  data <- read_csv(platform_paths[['facebook']])
} else if (selected_platform == 'reddit') {
  data <- read_csv(platform_paths[['reddit']], col_types = cols(post_id = col_skip(), user_id = col_skip(), num_people_cat = col_skip()))
  colnames(data) <- c('post_size', 'interaction_len', 'month_year')
  data$interaction_len <- data$interaction_len + 1
} else if (selected_platform == 'usenet') {
  data <- read_csv(platform_paths[['usenet']])
  colnames(data) <- c('post_size', 'interaction_len', 'month_year')
} else if (selected_platform == 'twitter') {
  data <- read_csv(platform_paths[['twitter']])
}

# Clean and filter data
data <- na.omit(data)
data$platform <- selected_platform

# Extract the year from 'month_year' column
data <- data %>%
  mutate(year = substr(month_year, 1, 4))

# Create uniform post size classes with a step of 10
data <- data %>%
  mutate(post_size_class = cut(log(post_size + 1), 
                                breaks = seq(0, log(max(data$post_size, na.rm = TRUE) + 1), length.out = 50), 
                                include.lowest = TRUE, 
                                right = FALSE))

# Group the interaction lengths for plotting
data$interaction_len <- cut(data$interaction_len, breaks = c(0, 1:10, Inf), labels = c(as.character(1:10), "10-nf"), right = FALSE)

# Calculate entropy of interaction_len for each post size class and year
entropy_data <- data %>%
  group_by(year, post_size_class) %>%
  summarise(
    entropy = -sum((table(interaction_len) / n()) * log(table(interaction_len) / n()), na.rm = TRUE),
    count = n(),
    .groups = 'drop'
  ) %>%
  filter(count >= 100)

# Set limits for the axes
x_limits <- levels(entropy_data$post_size_class)  # Get the levels for discrete x-axis
y_limits <- c(0, max(entropy_data$entropy, na.rm = TRUE))

# Directory and filename to save PDF
output_pdf <- paste0("/home/jacoponudo/Documents/Size_effects/PLT/4_size_entropy/", selected_platform, "_entropy_plots.pdf")

# Open PDF device
pdf(output_pdf, width = 8, height = 6)

# Loop through each year and plot
years <- unique(entropy_data$year)
for (yr in years) {
  yearly_data <- entropy_data %>% filter(year == yr)
  
  p <- ggplot(yearly_data, aes(x = post_size_class, y = entropy)) +
    geom_line(group = 1) +
    geom_point(size = 2) +
    scale_x_discrete(name = "Post Size Class (Uniform Bins)") +  # Use scale_x_discrete
    scale_y_continuous(name = "Entropy", limits = y_limits) +
    labs(title = paste("Entropy of Interaction Length by Post Size Class for", selected_platform, "in", yr)) +
    theme_minimal() +
    theme(axis.text.x = element_text(angle = 45, hjust = 1))
  
  print(p)  # Print each plot to the PDF
}

# Close the PDF device
dev.off()

# Plot for all years
p_all_years <- ggplot(entropy_data, aes(x = post_size_class, y = entropy, color = year)) +
  geom_line(aes(group = year)) +
  geom_point(size = 2) +
  scale_x_discrete(name = "Post Size Class (Uniform Bins)") +
  scale_y_continuous(name = "Entropy", limits = y_limits) +
  labs(title = paste("Entropy of Interaction Length by Post Size Class for", selected_platform, "all years")) +
  theme_minimal() +
  theme(axis.text.x = element_text(angle = 45, hjust = 1)) +
  scale_color_discrete(name = "Year")

# Print the combined plot
print(p_all_years)
