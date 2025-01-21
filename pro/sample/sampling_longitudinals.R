library(readr)
library(dplyr)
sample_posts <- read_csv("~/Documents/Size_effects/DATA/sample_posts.csv", 
                         col_types = cols(...1 = col_skip(), from_id = col_character(), 
                                          from_name = col_skip(), message = col_skip(), 
                                          type = col_skip(), link = col_skip(), 
                                          page_id = col_character()),col_select = c(from_id, post_id))
colnames(sample_posts)=c('page_id','post_id')
sample_posts <- distinct(sample_posts)

# Leggi solo le colonne 'from_id' e 'post_id' dal file CSV
sample_comments <- read_csv(
  "~/Documents/Size_effects/DATA/sample_comments.csv",
  col_types = cols(
    from_id = col_character(),
    post_id = col_character()
  ),
  col_select = c(from_id, post_id)
)


sample <- right_join(sample_posts, sample_comments, by = "post_id")
library(data.table) 
fwrite(sample, "~/Documents/Size_effects/DATA/sample_longitudinals.csv")
