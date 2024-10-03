library(readr)
library(ggplot2)
library(dplyr)
library(readr)
library(pscl)
platform='twitter'
format='interaction' # interaction or thread

# Questo script contiene: 
# - il passaggio dal thread di commenti a interaction df (ovvero ogni riga è un interazione e contene sia la len dell'intrazione che la size del thread)
# - plot della probabilità do fare un solo commento (~alpha) rispetto al numero di persone coinvolte in una conversazione
# - plot del numero mediano di commenti che si fanno condizionata rispetto ad aver fatto piu di un commento (lambda) rispetto al numero di persone coinvolte in una conversazione
# - modello zip per verificare questa relazione usando la size come predittore di alpha e lambda.

##  Tread to interaction
if (platform == 'facebook') {
  data <- read_csv("~/Documents/Size_effects/DATA/sample_interactions.csv", col_types = cols(...1 = col_skip()))
} else if (platform == 'reddit') {
  data <- read_csv("~/Documents/Size_effects/RPR/reddit_size_vs_interaction.csv", col_types = cols(post_id = col_skip(), user_id = col_skip(), num_people_cat = col_skip()))
} else if (platform == 'usenet') {
  data <- read_csv("/home/jacoponudo/Documents/Size_effects/DATA/usenet/PRO_usenet.csv")
} else if (platform == 'twitter') {
  data <- read_csv("/home/jacoponudo/Documents/Size_effects/DATA/twitter/PRO_twitter.csv")
}

data=na.omit(data)


colnames(data)=c('post_size', 'interaction_len')


max_post_size <- max(data$post_size, na.rm = TRUE)
breaks <- seq(0, max_post_size, by = 20)

# Crea le classi di post_size
data <- data %>%
  mutate(post_size_class = cut(post_size, breaks = breaks, include.lowest = TRUE))

# Calcola la media degli alpha (interaction_len)
percentage_ones <- data %>%
  group_by(post_size_class) %>%
  summarise(percentage = mean(interaction_len == 1, na.rm = TRUE))

percentage_ones=na.omit(percentage_ones)
# Visualizzazione
ggplot(data, aes(x = post_size_class, y = interaction_len)) +
  geom_line(data = percentage_ones, aes(y = percentage), color = "orange", group = 1) +
  geom_point(data = percentage_ones, aes(y = percentage), color = "orange", size = 5) +
  scale_y_continuous(name = "Alpha", limits = c(0, 1.1)) +
  labs(x = "Post Size Class", title = "Interaction Length by Post Size Class with Percentage of 1s") +
  theme_minimal() +
  theme(axis.text.x = element_text(angle = 45, hjust = 1))