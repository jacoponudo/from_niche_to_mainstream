# 0
## Importo tutti i pacchetti 

#install.packages("dplyr")
#install.packages("purrr")
#install.packages("progress") 

library(dplyr)
library(purrr)
library(progress)

pb <- progress_bar$new(
  format = "  processing [:bar] :percent eta: :eta",
  total = length(file_list), clear = FALSE, width = 60
)

filter_data_page <- function(file) {
  data <- read.csv(file, colClasses = "character")
  filtered_data <- data %>% filter(from_id %in% pages)
  pb$tick()
  
  return(filtered_data)
}

pb <- progress_bar$new(
  format = "  processing [:bar] :percent eta: :eta",
  total = length(file_list), clear = FALSE, width = 60
)

filter_data_post<- function(file) {
  data <- read.csv(file, colClasses = "character")
  filtered_data <- data %>% filter(post_id %in% posts)
  pb$tick()
  return(filtered_data)
}

pb <- progress_bar$new(
  format = "  processing [:bar] :percent eta: :eta",
  total = length(file_list), clear = FALSE, width = 60
)

