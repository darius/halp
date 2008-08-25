;; NOTE: You need to change the following variable to the directory
;; containing this file:
(defvar halp-helpers-directory "/Users/darius/git/halp/"
  "Directory where Halp helper scripts are installed.")

(defun halp-add-hook (hook map-name key halp-update-function)
  (add-hook hook
            `(lambda ()
               (define-key ,map-name ',key ',halp-update-function))))

(halp-add-hook 'sh-mode-hook 'sh-mode-map "\M-i" 'halp-update-sh)
(halp-add-hook 'python-mode-hook 'python-mode-map "\M-i" 'halp-update-python)
(halp-add-hook 'haskell-mode-hook 'haskell-mode-map "\M-i" 'halp-update-haskell)
(halp-add-hook 'literate-haskell-mode-hook 'literate-haskell-mode-map "\M-i"
               'halp-update-literate-haskell)

;; The rest of this file shouldn't need editing.

;; Copyright 2006 Darius Bacon <darius@wry.me>
;; Distributed under the terms of the MIT X License, found at
;; http://www.opensource.org/licenses/mit-license.php

(require 'cl)

(defun halp-update-sh ()
  (interactive)
  (halp-update (concat halp-helpers-directory "sh-halp.sh") '()))

(defun halp-update-python ()
  (interactive)
  (halp-update (concat halp-helpers-directory "pyhalp.py") '()))

(defun halp-update-haskell ()
  (interactive)
  (halp-update (concat halp-helpers-directory "ghcihalp.py") '(".hs")))

(defun halp-update-literate-haskell ()
  (interactive)
  (halp-update (concat halp-helpers-directory "ghcihalp.py") '(".lhs")))

(defun halp-update (command args)
  "Update the current buffer using an external helper program."
  (interactive)
  (let ((output (halp-get-output-buffer)))
;;    (call-process-region (point-min) (point-max) "cat" t t)
    (let ((rc (apply 'call-process-region
                     (point-min) (point-max) command nil output nil 
                     args)))
      (cond ((zerop rc)                 ;success
             (halp-update-current-buffer output)
             (message "hooray"))
            ((numberp rc)
             (message "Helper process failed"))
            (t (message rc))))))

(defun halp-get-output-buffer ()
  "Return an empty buffer dedicated (hopefully) to halp's use."
  (let ((output (get-buffer-create "*halp-output*")))
    (save-current-buffer
      (set-buffer output)
      (erase-buffer))
    output))

(defun halp-update-current-buffer (output)
  "Update the current buffer using the output buffer."
  ;; Currently we just overwrite the original buffer with the output.
  ;; You could get the same effect, more easily, by setting
  ;; call-process-region's output buffer to t. (Commented out.)  But
  ;; we'll soon want to update things more intelligently.
  (let ((p (point)))
    (erase-buffer)
    (insert-buffer output)
    (goto-char p)))

;; Wrap-up

(provide 'halp)
