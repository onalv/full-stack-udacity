import media
import fresh_tomatoes

interstellar = media.Movie( "Interstellar",
                            "A team of explorers travel through a wormhole in space in an attempt to ensure humanity's survival",
                            "http://static.rogerebert.com/uploads/movie/movie_poster/interstellar-2014/large_lbGGuk9K1kNQqDabaMyFz1L9iTg.jpg",
                            "https://www.youtube.com/watch?v=zSWdZVtXT7E")

inception = media.Movie("Inception",
                        "A thief, who steals corporate secrets through use of dream-sharing technology, is given the inverse task of planting an idea into the mind of a CEO",
                        "https://images-na.ssl-images-amazon.com/images/M/MV5BMjAxMzY3NjcxNF5BMl5BanBnXkFtZTcwNTI5OTM0Mw@@._V1_SY1000_CR0,0,675,1000_AL_.jpg",
                        "https://www.youtube.com/watch?v=66TuSJo4dZM")

matrix = media.Movie("Matrix",
                     "A computer hacker learns from mysterious rebels about the true nature of his reality and his role in the war against its controllers",
                     "https://images-na.ssl-images-amazon.com/images/M/MV5BNzQzOTk3OTAtNDQ0Zi00ZTVkLWI0MTEtMDllZjNkYzNjNTc4L2ltYWdlXkEyXkFqcGdeQXVyNjU0OTQ0OTY@._V1_SY1000_CR0,0,665,1000_AL_.jpg",
                     "https://www.youtube.com/watch?v=m8e-FF8MsqU")

django = media.Movie("Django",
                     "With the help of a German bounty hunter , a freed slave sets out to rescue his wife from a brutal Mississippi plantation owner",
                     "https://images-na.ssl-images-amazon.com/images/M/MV5BMjIyNTQ5NjQ1OV5BMl5BanBnXkFtZTcwODg1MDU4OA@@._V1_SY1000_CR0,0,674,1000_AL_.jpg",
                     "https://www.youtube.com/watch?v=eUdM9vrCbow")

the_great_gatsby = media.Movie("The Great Gatsby",
                               "A writer and wall street trader, Nick, finds himself drawn to the past and lifestyle of his millionaire neighbor, Jay Gatsby",
                               "https://images-na.ssl-images-amazon.com/images/M/MV5BMTkxNTk1ODcxNl5BMl5BanBnXkFtZTcwMDI1OTMzOQ@@._V1_SY1000_SX666_AL_.jpg",
                               "https://www.youtube.com/watch?v=rARN6agiW7o")

the_departed = media.Movie("The Departed",
                           "An undercover cop and a mole in the police attempt to identify each other while infiltrating an Irish gang in South Boston",
                           "https://images-na.ssl-images-amazon.com/images/M/MV5BMTI1MTY2OTIxNV5BMl5BanBnXkFtZTYwNjQ4NjY3._V1_.jpg",
                           "https://www.youtube.com/watch?v=SGWvwjZ0eDc")

the_godfather = media.Movie("The Godfather",
                            "The aging patriarch of an organized crime dynasty transfers control of his clandestine empire to his reluctant son",
                            "https://images-na.ssl-images-amazon.com/images/M/MV5BZTRmNjQ1ZDYtNDgzMy00OGE0LWE4N2YtNTkzNWQ5ZDhlNGJmL2ltYWdlL2ltYWdlXkEyXkFqcGdeQXVyNjU0OTQ0OTY@._V1_SY1000_CR0,0,704,1000_AL_.jpg",
                            "https://www.youtube.com/watch?v=sY1S34973zA")

movies = [interstellar, inception, matrix, django, the_great_gatsby, the_departed, the_godfather]

fresh_tomatoes.open_movies_page(movies)