;; Copyright 2006, 2008 Darius Bacon <darius@wry.me>
;; Distributed under the terms of the MIT X License, found at
;; http://www.opensource.org/licenses/mit-license.php

;; If for some reason you move the helper programs like pyhalp.py to a
;; different directory (not the one this file is loaded from) then set
;; this variable:
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
                 'halp-update-literate-haskell)
  (halp-add-hook 'javascript-mode-hook 'javascript-mode-map "\M-i"
                 'halp-update-javascript))

(defun halp-add-hook (hook map-name key halp-update-function)
  (add-hook hook
            `(lambda ()
               (define-key ,map-name ',key ',halp-update-function))))

(defun halp-update-sh ()
  (interactive)
  (halp-update-relative "sh-halp.sh" '()))

(defun halp-update-python ()
  (interactive)
  (halp-find-helpers-directory)
  (halp-update/diff (concat halp-helpers-directory 
			    (pick-by-os "pyhalp.py" "pyhalp.bat")) 
                    (list (buffer-name (current-buffer)))))

(defun halp-update-javascript ()
  (interactive)
  (halp-find-helpers-directory)
  (halp-update/diff (concat halp-helpers-directory "v8halp.py") '()))

(defun halp-update-haskell ()
  (interactive)
  (halp-update-relative (pick-by-os "ghcihalp.py" "ghcihalp.bat") '(".hs")))

(defun halp-update-literate-haskell ()
  (interactive)
  (halp-update-relative (pick-by-os "ghcihalp.py" "ghcihalp.bat") '(".lhs")))

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
              (file-name-directory filename))))))


;; Running a helper command and applying its output

(defun halp-update (command args)
  "Update the current buffer using an external helper program."
  (interactive)
  (message "Halp starting...")
  (let ((output (halp-get-output-buffer)))
;;    (call-process-region (point-min) (point-max) "cat" t t)
    (let ((rc (apply 'call-process-region
                     (point-min) (point-max) command nil output nil 
                     args)))
      (cond ((zerop rc)                 ;success
             (halp-update-current-buffer output)
             (message "Halp starting... done"))
            ((numberp rc)
             (message "Halp starting... helper process failed"))
            (t (message rc))))))

(defun halp-update/diff (command args)
  "Update the current buffer using an external helper program
that outputs a diff."
  (interactive)
  (message "Halp starting...")
  (let ((output (halp-get-output-buffer)))
    (let ((rc (apply 'call-process-region
                     (point-min) (point-max) command nil output nil 
                     args)))
      (cond ((zerop rc)                 ;success
             (halp-update-current-buffer/diff output)
             (message "Halp starting... done"))
            ((numberp rc)
             (message "Halp starting... helper process failed"))
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

(defun halp-update-current-buffer/diff (output)
  (save-excursion
    (halp-apply-diff (current-buffer) output)))


;;; Parsing and applying a diff

(defun halp-apply-diff (to-buffer from-buffer)
  (setq halp-argh '())
  (save-current-buffer
    (set-buffer from-buffer)
    (goto-char (point-min))
    (while (not (eobp))
      (multiple-value-bind (lineno n-del start end) (halp-scan-chunk)
        (halp-dbg (list 'chunk lineno n-del start end))
        (set-buffer to-buffer)
        (goto-line lineno)
        (when (and (eobp) (/= (preceding-char) 10))
          ; No newline at end of buffer; add it. Otherwise the
          ; code below will delete the last line.
          (insert-char 10 1))
        (multiple-value-bind (start1 end1) (halp-scan-lines n-del)
          (delete-region start1 end1)
          (halp-dbg (list 'deleted n-del start1 end1)))
        (insert-buffer-substring from-buffer start end)
        (set-buffer from-buffer)))))

(defun halp-dbg (x)
  (setq halp-argh (cons x halp-argh)))

(defvar halp-argh nil)

(defun halp-scan-chunk ()
  (let* ((lineno (halp-scan-number))
         (n-del (halp-scan-number))
         (n-ins (halp-scan-number)))
    (forward-line)
    (multiple-value-bind (start end) (halp-scan-lines n-ins)
      (values lineno n-del start end))))

(defun halp-scan-lines (n)
  (let ((start (point)))
    (forward-line n)
    (values start (point))))

(defun halp-scan-number ()
  (string-to-number (halp-scan-word)))

(defun halp-scan-word ()
  (let ((start (point)))
    (forward-word 1)
    (halp-from start)))

(defun halp-from (start)
  (buffer-substring start (point)))

(defun pick-by-os (default-file windows-file)
  (if (eq system-type 'windows-nt)
      windows-file
    default-file))

;; Wrap-up

(halp-add-all-hooks)
(provide 'halp)
