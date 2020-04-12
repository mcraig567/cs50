SELECT name FROM people WHERE people.id IN (SELECT stars.person_id FROM stars WHERE stars.movie_id IN (SELECT id from movies WHERE title = "Toy Story"));
