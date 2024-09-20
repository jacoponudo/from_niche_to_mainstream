# Questo script si concentra su estrarre i longitudinali dell'attività attorno a 10 pagine da elements di matteo 
# Il lavoro è diviso in 4 sezioni, la prima legge le pagine (page_id), la seconda legge tutti i post di queste pagine (post_id), la terza tutti i like ai post di queste pagine e ritorna un dataset e la quarta tutti i commenti.


# 1 
## Seleziono la lista di pagine 
pages  <- c("185885781448435", "131498596889079", "143728442343553", "37791069588", 
                "129869803756134", "129892740363306", "172730922764856", "456049707755135", 
                "139471392786597", "291155398585")


# 2
## Seleziono la lista di post per ciascuna pagina 
folder_path <- "/media/gabett/Elements/facebook_news/OriginalData/PostsCSV/"
file_list <- list.files(path = folder_path, pattern = "*.csv", full.names = TRUE)
all_filtered_data <- map_df(file_list, filter_data)
write.csv(all_filtered_data,'~/Documents/repository/size-effect/SAM/sample/sample_posts.csv')