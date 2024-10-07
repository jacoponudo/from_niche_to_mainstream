library(readr)
library(dplyr)
library(ggplot2)

data <- read_csv("/home/jacoponudo/Documents/Size_effects/DATA/interacions/facebook_outreach_vs_interaction.csv", 
                                             col_types = cols(...1 = col_skip(), post_id = col_skip(), 
                                                              alpha = col_skip()))
data <- na.omit(data)
colnames(data) <- c("interaction_len", "post_size")
platform <- 'facebook'

# Clean and filter data
data <- na.omit(data)

# Create uniform post size classes with a step of 10
data <- data %>%
  mutate(post_size_class = cut(log(post_size + 1), 
                                breaks = seq(0, log(max(data$post_size, na.rm = TRUE) + 1), length.out = 300), 
                                include.lowest = TRUE, 
                                right = FALSE))

# Group the interaction lengths for plotting
data$interaction_len <- cut(data$interaction_len, breaks = c(0, 1:20, Inf), labels = c(as.character(1:20), "20-nf"), right = FALSE)

# Calculate entropy of interaction_len for each post size class
entropy_data <- data %>%
  group_by(post_size_class) %>%
  summarise(
    entropy = -sum((table(interaction_len) / sum(table(interaction_len))) * log(table(interaction_len) / sum(table(interaction_len))), na.rm = TRUE),
    count = n(),
    .groups = 'drop'
  ) %>%
  filter(count >= 100)

# Set limits for the axes
x_limits <- levels(entropy_data$post_size_class)
y_limits <- c(0, max(entropy_data$entropy, na.rm = TRUE))

# Directory and filename to save PDF
output_pdf <- paste0("/home/jacoponudo/Documents/Size_effects/PLT/4_size_entropy/", platform, "_entropy_plots.pdf")


p <- ggplot(entropy_data, aes(x = post_size_class, y = entropy)) +
  geom_line(group = 1) +
  geom_point(size = 2) +
  scale_x_discrete(name = "Post Size Class (Uniform Bins)") +
  scale_y_continuous(name = "Entropy", limits = y_limits) +
  labs(title = paste("Entropy of Interaction Length by Post Size Class for", platform)) +
  theme_minimal() +
  theme(axis.text.x = element_text(angle = 45, hjust = 1))
p
