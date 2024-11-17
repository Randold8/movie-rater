import tkinter as tk
from tkinter import ttk
from tkinter import font as tkfont
import csv
import random
import math

class MovieRatingApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Movie Rating App")
        self.master.geometry("400x500")
        self.master.configure(bg="#f0f0f0")

        # Initialize movies and ratings
        self.movies = self.load_movies()
        self.ratings = {}

        self.style = ttk.Style()
        self.style.theme_use("clam")

        main_font = tkfont.Font(family="Helvetica", size=12)
        title_font = tkfont.Font(family="Helvetica", size=16, weight="bold")

        # Main frame
        main_frame = ttk.Frame(master, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Movie title frame with fixed height
        self.movie_frame = ttk.Frame(main_frame, height=80)
        self.movie_frame.pack(fill=tk.X, pady=(0, 20))
        self.movie_frame.pack_propagate(False)  # Prevent the frame from shrinking

        self.movie_label = ttk.Label(self.movie_frame, text="", font=title_font, wraplength=360, justify="center")
        self.movie_label.pack(expand=True)

        # Rating frame
        rating_frame = ttk.Frame(main_frame)
        rating_frame.pack(fill=tk.X, pady=10)

        rating_label = ttk.Label(rating_frame, text="Your Rating (1-10):", font=main_font)
        rating_label.pack(side=tk.LEFT, padx=(0, 10))

        self.rating_var = tk.StringVar()
        self.rating_entry = ttk.Entry(rating_frame, textvariable=self.rating_var, width=5, font=main_font)
        self.rating_entry.pack(side=tk.LEFT)

        # Buttons frame
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill=tk.X, pady=10)

        self.submit_button = ttk.Button(buttons_frame, text="Submit Rating", command=self.submit_rating)
        self.submit_button.pack(side=tk.LEFT, expand=True, padx=(0, 5))

        self.havent_seen_button = ttk.Button(buttons_frame, text="Haven't Seen", command=self.havent_seen)
        self.havent_seen_button.pack(side=tk.LEFT, expand=True, padx=(5, 0))

        # Popularity slider
        slider_frame = ttk.Frame(main_frame)
        slider_frame.pack(fill=tk.X, pady=(20, 10))

        slider_label = ttk.Label(slider_frame, text="Popularity Bias:", font=main_font)
        slider_label.pack(side=tk.LEFT)

        self.popularity_var = tk.DoubleVar()
        self.popularity_var.set(0.3)  # Default to 30%
        self.popularity_slider = ttk.Scale(slider_frame, from_=0, to=1, orient='horizontal',
                                           variable=self.popularity_var, command=self.update_popularity_label)
        self.popularity_slider.pack(side=tk.LEFT, expand=True, padx=(10, 0))

        self.popularity_label = ttk.Label(slider_frame, text="30%", font=main_font, width=5)
        self.popularity_label.pack(side=tk.LEFT)

        # Status message
        self.status_var = tk.StringVar()
        self.status_label = ttk.Label(main_frame, textvariable=self.status_var, font=main_font)
        self.status_label.pack(pady=(20, 0))

        self.display_random_movie()


    def update_popularity_label(self, *args):
        self.popularity_label.config(text=f"{int(self.popularity_var.get() * 100)}%")

    def load_movies(self):
        movies = {}
        encodings = ['utf-8', 'latin-1']
        for encoding in encodings:
            try:
                with open('movies.csv', 'r', encoding=encoding) as file:
                    reader = csv.reader(file)
                    next(reader)  # Skip header row
                    for row in reader:
                        if len(row) >= 2:
                            movie_id = row[0]
                            movie_name = row[1]
                            votes = 0
                            if len(row) >= 8:
                                try:
                                    votes = int(row[7])
                                except ValueError:
                                    votes = 0
                            movies[movie_id] = {'name': movie_name, 'votes': votes}
                return movies
            except UnicodeDecodeError:
                continue
        raise ValueError("Unable to read the CSV file with the attempted encodings.")

    def display_random_movie(self):
        available_movies = [movie for movie in self.movies if movie not in self.ratings]
        if available_movies:
            weights = self.calculate_weights(available_movies)
            movie_id = random.choices(available_movies, weights=weights, k=1)[0]
            self.current_movie = movie_id
            self.movie_label.config(text=self.movies[movie_id]['name'])
        else:
            self.movie_label.config(text="No more movies available")

    def calculate_weights(self, available_movies):
        popularity_bias = self.popularity_var.get()
        votes = [self.movies[movie]['votes'] for movie in available_movies]
        max_votes = max(votes)
        weights = [((v / max_votes) ** (popularity_bias * 2)) for v in votes]
        return weights

    def update_movie(self, *args):
        self.popularity_label.config(text=f"{int(self.popularity_var.get() * 100)}%")
        self.display_random_movie()


    def submit_rating(self):
        rating = self.rating_var.get()
        if rating.isdigit() and 1 <= int(rating) <= 10:
            self.ratings[self.current_movie] = int(rating)
            self.save_rating(int(rating))
            self.rating_var.set("")
            self.status_var.set("Rating submitted successfully!")
            self.status_label.config(foreground="green")
            self.display_random_movie()  # Only fetch new movie after rating
        else:
            self.status_var.set("Please enter a valid rating (1-10)")
            self.status_label.config(foreground="red")

    def havent_seen(self):
        self.ratings[self.current_movie] = "Haven't Seen"
        self.save_rating("Haven't Seen")
        self.status_var.set("Response recorded: Haven't Seen")
        self.status_label.config(foreground="green")
        self.display_random_movie()  # Only fetch new movie after response

    def save_rating(self, rating):
        with open('ratings.csv', 'a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow([self.current_movie, self.movies[self.current_movie]['name'], rating])

root = tk.Tk()
app = MovieRatingApp(root)
root.mainloop()

