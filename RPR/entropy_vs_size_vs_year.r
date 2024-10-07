library(readr)
library(ggplot2)
library(dplyr)

# Define the platform you want to analyze
selected_platform <- 'facebook'  # You can change this to 'reddit', 'usenet', 'twitter', etc.

# List of available platforms (optional, for reference)
platforms <- c('facebook', 'reddit', 'usenet', 'twitter')

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
data$platform <- selected_platform  # Add platform as a column

# Extract the year from 'month_year' column
data <- data %>%
  mutate(year = substr(month_year, 1, 4))  # Extract the year (first 4 characters)

# Create uniform post size classes with a step of 10
data <- data %>%
  mutate(post_size_class = cut(log(post_size + 1),  # Adding 1 to avoid log(0)
                                breaks = seq(0, log(max(data$post_size, na.rm = TRUE) + 1), length.out = 50), 
                                include.lowest = TRUE, 
                                right = FALSE))

# Group the interaction lengths for plotting
data$interaction_len <- cut(data$interaction_len, breaks = c(0, 1:50, Inf), labels = c(as.character(1:50), "50-nf"), right = FALSE)

# Calculate entropy of interaction_len for each post size class and year
entropy_data <- data %>%
  group_by(year, post_size_class) %>%
  summarise(
    entropy = -sum((table(interaction_len) / n()) * log(table(interaction_len) / n()), na.rm = TRUE),
    count = n(),
    .groups = 'drop'
  ) %>%
  filter(count >= 100) # Keep only classes with at least 100 observations

# Set limits for the axes
x_limits <- range(as.numeric(levels(entropy_data$post_size_class)), na.rm = TRUE)
y_limits <- c(0, max(entropy_data$entropy, na.rm = TRUE))

# Directory and filename to save PDF
output_pdf <- "/home/jacoponudo/Documents/Size_effects/PLT/4_size_entropy/"+selected_platform+"_entropy_plots.pdf"

# Open PDF device
pdf(output_pdf, width = 8, height = 6)

# Loop through each year and plot
years <- unique(entropy_data$year)
for (yr in years) {
  yearly_data <- entropy_data %>% filter(year == yr)
  
  p <- ggplot() +
    geom_line(data = yearly_data, aes(x = post_size_class, y = entropy, group = 1)) +
    geom_point(data = yearly_data, aes(x = post_size_class, y = entropy), size = 2) +
    scale_x_continuous(name = "Post Size Class (Uniform Bins)", limits = x_limits) +
    scale_y_continuous(name = "Entropy", limits = y_limits) +
    labs(title = paste("Entropy of Interaction Length by Post Size Class for", selected_platform, "in", yr)) +
    theme_minimal() +
    theme(axis.text.x = element_text(angle = 45, hjust = 1))
  
  print(p)  # Print each plot to the PDF
}

# Close the PDF device
dev.off()

ggplot() +
  geom_line(data = entropy_data, aes(x = post_size_class, y = entropy, color = year, group = year)) +
  geom_point(data = entropy_data, aes(x = post_size_class, y = entropy, color = year), size = 2) +
  scale_x_discrete(name = "Post Size Class (Uniform Bins)") +  # Usa scale_x_discrete per valori discreti
  scale_y_continuous(name = "Entropy", limits = y_limits) +
  labs(title = paste("Entropy of Interaction Length by Post Size Class for", selected_platform, "all years")) +
  theme_minimal() +
  theme(axis.text.x = element_text(angle = 45, hjust = 1)) +
  scale_color_discrete(name = "Year")
