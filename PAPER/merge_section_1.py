import matplotlib.pyplot as plt
import matplotlib.image as mpimg

# File paths
images = [
    '/home/jacoponudo/Documents/Size_effects/PAPER/output/1_section/1_users_in_thread_gab.png',
    '/home/jacoponudo/Documents/Size_effects/PAPER/output/1_section/1_users_in_thread_reddit.png',
    '/home/jacoponudo/Documents/Size_effects/PAPER/output/1_section/2_lifetime_thread_twitter.png',
    '/home/jacoponudo/Documents/Size_effects/PAPER/output/1_section/2_lifetime_thread_usenet.png'
]

# Create a figure to display the plots
fig, axes = plt.subplots(2, 2, figsize=(12, 12))

# Read and display each image
for ax, img_path in zip(axes.flat, images):
    img = mpimg.imread(img_path)
    ax.imshow(img)
    ax.axis('off')  # Hide axes for a cleaner look

# Adjust layout
plt.tight_layout()

# Save the combined image
combined_image_path = '/home/jacoponudo/Documents/Size_effects/PAPER/output/1_section/1_users_in_thread.png'
plt.savefig(combined_image_path)

# Show the plot
plt.show()
