# Carica il file .rData
load('/media/jacoponudo/Elements/facebook_news/OriginalData/all_comments.rData')

# Campionamento di 1,000,000 di valori unici di post_id
sampled_post_ids <- sample(unique(all_comments$post_id), size = 10, replace = FALSE)

# Filtra il sottoinsieme con i post_id campionati
comments_sampled_subset <- all_comments[all_comments$post_id %in% sampled_post_ids, ]

# Libreria Arrow per il formato parquet
library(arrow)

# Imposta il numero di righe per ciascun batch
batch_size <- 1  

# Percorso del file di output
output_file <- "/home/jacoponudo/documents/size/data/facebook/facebook_raw_data.parquet"

# Inizializza il file
write_parquet(comments_sampled_subset[1:batch_size, ], output_file)

# Scrivi in batch
for (start_row in seq(batch_size + 1, nrow(comments_sampled_subset), by = batch_size)) {
  end_row <- min(start_row + batch_size - 1, nrow(comments_sampled_subset))
  batch <- comments_sampled_subset[start_row:end_row, ]
  write_parquet(batch, output_file, append = TRUE) # Usa append per aggiungere al file esistente
}
