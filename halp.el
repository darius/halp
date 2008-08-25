;; Copyright 2006, 2008 Darius Bacon <darius@wry.me>
;; Distributed under the terms of the MIT X License, found at
;; http://www.opensource.org/licenses/mit-license.php

;; If for some reason you move the helper programs like pyhalp.py to a
;; different directory (not the one this file is in) then set this
;; variable:
(defvar halp-helpers-directory nil
  "Directory where Halp helper scripts are installed.")

;; The rest of this file shouldn't need editing.

(require 'cl)

(defun halp-add-all-hooks ()
  (halp-add-hook 'sh-mode-hook 'sh-mode-map "\M-i" 'halp-update-sh)
  ; Python mode might be called either py-mode or python-mode:
  (halp-add-hook 'py-mode-hook 'py-mode-map "\M-i" 'halp-update-python)
  (halp-add-hook 'python-mode-hook 'python-mode-map "\M-i" 'halp-update-python)
  (halp-add-hook 'haskell-mode-hook 'haskell-mode-map "\M-i"
                 'halp-update-haskell)
  (halp-add-hook 'literate-haskell-mode-hook 'literate-haskell-mode-map "\M-i"
                 'halp-update-literate-haskell))

(defun halp-add-hook (hook map-name key halp-update-function)
  (add-hook hook
            `(lambda ()
               (define-key ,map-name ',key ',halp-update-function))))

(defun halp-update-sh ()
  (interactive)
  (halp-update-relative "sh-halp.sh" '()))

(defun halp-update-python ()
  (interactive)
  (halp-update-relative "pyhalp.py" '()))

(defun halp-update-haskell ()
  (interactive)
  (halp-update-relative "ghcihalp.py" '(".hs")))

(defun halp-update-literate-haskell ()
  (interactive)
  (halp-update-relative "ghcihalp.py" '(".lhs")))

(defun halp-update-relative (command args)
  (halp-find-helpers-directory)
  (halp-update (concat halp-helpers-directory command) args))

(defun halp-find-helpers-directory ()
  "Make halp-helpers-directory point to the directory it was
loaded from, if it's not yet initialized."
  (unless halp-helpers-directory
    (let ((filename (symbol-file 'halp-helpers-directory)))
      (when filename
        (setq halp-helpers-directory 
              (halp-filename-directory filename))))))

(defun halp-filename-directory (filename)
  "Return the directory part of a filename."
  (replace-regexp-in-string "/[^/]*$" "/" filename))

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

(halp-add-all-hooks)
(provide 'halp)
