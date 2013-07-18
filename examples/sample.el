;; Expressions followed by ';;. ' get results placed there.
;; Try running M-x halp-update-emacs-lisp now.

(+ 2 3)  ;;.

(defun hotpo (n)
  "Silly example function: half or triple plus one."
  (if (evenp n)
      (/ n 2)
    (1+ (* 3 n))))

(hotpo 5) ;;.
(hotpo 6) ;;.
