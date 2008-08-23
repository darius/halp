Here's a problem from Brian Hayes's Computing Science column.

A perfect median of a sequence of consecutive integers is an element 
where the sum of the preceding elements equals the sum of the
following ones.

> isPerfectMedian m n = sum [1..m-1] == sum [m+1..n]

--- isPerfectMedian 6 8
-- | True
--- isPerfectMedian 7 9
-- | False

Let's try finding some, in a really stupid way, to start.

> findMediansSlowly limit =
>     [(m, n) | n <- [1..limit], m <- [1..n-1], isPerfectMedian m n]

--- findMediansSlowly 50
-- | [(6,8),(35,49)]

OK, a little bit cleverer now:

> faster limit = 
>   concat $ map (checkMedian limit) [2..limit]

> checkMedian limit m =
>   let below = ((m-1) * m) `div` 2
>       (n, above) = findAbove m below
>   in if below == above
>      then [(m, n)]       
>      else []

--- faster 500
-- | [(6,8),(35,49),(204,288)]

> findAbove m below =
>   head $ dropWhile (\ (i, s) -> s < below)
>                    (iterate (\ (i, s) -> (i+1, s+i+1)) (m, 0))

--- findAbove 6 15
-- | (8,15)

(Pardon the horrible code; even I can write better, but the idea was
(to play with Halp as a tool and not focus on code quality.)
