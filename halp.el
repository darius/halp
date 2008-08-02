; Copyright 2006 by Darius Bacon
; Distributed under the terms of the MIT X License, found at
; http://www.opensource.org/licenses/mit-license.php

(require 'cl)

(defvar halp-helpers-directory "~/src/halp/"
  "Directory where Halp helper scripts are installed.")

(defun halp-update (command)
  "Update the current buffer using an external helper program."
  (interactive)
  (let ((output (halp-get-output-buffer)))
;;    (call-process-region (point-min) (point-max) "cat" t t)
    (let ((rc (call-process-region (point-min) (point-max)
                                   command nil output)))
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
  (save-excursion
    (erase-buffer)
    (insert-buffer output)))

;; Wrap-up

(defun halp-add-hook (hook map-name key helper-command)
  (add-hook hook
            `(lambda ()
               (define-key ,map-name ',key
                 (lambda ()
                   (interactive)
                   (halp-update ',helper-command))))))

(halp-add-hook 'sh-mode-hook 'sh-mode-map
               "\M-i" (concat halp-helpers-directory "sh-halp.sh"))

(halp-add-hook 'haskell-mode-hook 'haskell-mode-map
               "\M-i" (concat halp-helpers-directory "ghci-halp.sh"))

(provide 'halp)
