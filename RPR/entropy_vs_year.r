library(readr)
library(ggplot2)
library(dplyr)

platform = 'twitter'

# Carica i dati in base alla piattaforma
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

# Converti la colonna 'month_year' in formato data
summary_per_month$month_year <- as.Date(paste0(summary_per_month$month_year, "-01"), "%Y-%m-%d")
summary_per_month$log_avg_post_size = log(summary_per_month$avg_post_size)

# Crea il grafico con ggplot2 per maggiore eleganza
ggplot(summary_per_month, aes(x = month_year)) +
  # Linea per l'entropia
  geom_line(aes(y = entropy, color = "Entropia"), size = 1.5) +
  # Linea per la dimensione media dei post (in scala logaritmica)
  geom_line(aes(y = log_avg_post_size, color = "Dimensione media (log)"), size = 1.5) +
  # Aggiungi etichette e titolo
  labs(title = paste("Entropia e Dimensione media dei post per", platform),
       x = "Mese", 
       y = "Valore",
       color = "Legenda") +
  # Stile del tema
  theme_minimal() +
  # Aggiungi una palette di colori più legata a Facebook
  scale_color_manual(values = c("Entropia" = "blue", "Dimensione media (log)" = "gray40")) +
  # Aggiungi griglia
  theme(panel.grid.major = element_line(color = "gray85"),
        panel.grid.minor = element_line(color = "gray90"),
        plot.title = element_text(size = 14, face = "bold"),
        legend.position = "top")


#plot(summary_per_month$entropy,summary_per_month$log_avg_post_size)