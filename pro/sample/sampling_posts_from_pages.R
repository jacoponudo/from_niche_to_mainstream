# Questo script si concentra su estrarre i longitudinali dell'attività attorno a 10 pagine da elements di matteo 
# Il lavoro è diviso in 4 sezioni, la prima legge le pagine (page_id), la seconda legge tutti i post di queste pagine (post_id), la terza tutti i like ai post di queste pagine e ritorna un dataset e la quarta tutti i commenti.

# 1 
## Seleziono la lista di pagine 
load("/media/jacoponudo/Elements/facebook_news/OriginalData/page_info.RData")
pages  <- sample(page_info$fb_id,100)

# 2
## Seleziono la lista di post per ciascuna pagina 
folder_path <- "/media/jacoponudo/Elements/facebook_news/OriginalData/PostsCSV/"
file_list <- list.files(path = folder_path, pattern = "*.csv", full.names = TRUE)
all_filtered_data <- map_df(file_list, filter_data_page)
write.csv(all_filtered_data,'~/Documents/Size_effects/DATA/sample_posts.csv')

# 3 
## Seleziono tutti i commenlibrary(data.table) 
posts=read.csv('~/Documents/Size_effects/DATA/sample_posts.csv',colClasses = "character")
posts=unique(posts$post_id)
folder_path <- "/media/jacoponudo/Elements/facebook_news/OriginalData/CommentsCSV/"
file_list <- list.files(path = folder_path, pattern = "*.csv", full.names = TRUE)
all_filtered_data <- map_df(file_list, filter_data_post)
fwrite(all_filtered_data, "~/Documents/Size_effects/DATA/sample_comments.csv")

# 4
## Seleziono tutti i like ai post gia filtrati 
posts=read.csv('~/Documents/Size_effects/DATA/sample_posts.csv',colClasses = "character")
posts=unique(posts$post_id)
folder_path <- "/media/jacoponudo/Elements/facebook_news/OriginalData/LikesCSV/"
file_list <- list.files(path = folder_path, pattern = "*.csv", full.names = TRUE)
all_filtered_data <- map_df(file_list, filter_data_post)
fwrite(all_filtered_data, "~/Documents/Size_effects/DATA/sample_likes.csv")

