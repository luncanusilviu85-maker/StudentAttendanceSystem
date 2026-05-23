/**
 * attendance.js — Client-side helpers for the attendance marking page.
 * Colour-highlights rows based on selected radio status.
 */

(function () {
  'use strict';

  const STATUS_COLORS = {
    present: '#f0fdf4',
    absent:  '#fef2f2',
    late:    '#fffbeb',
  };

  function highlightRow(radio) {
    const row    = radio.closest('tr');
    const status = radio.value;
    row.style.background = STATUS_COLORS[status] || '';
  }

  function initRows() {
    document.querySelectorAll('.attendance-table tr').forEach(function (row) {
      const checked = row.querySelector('input[type="radio"]:checked');
      if (checked) highlightRow(checked);
    });
  }

  document.addEventListener('change', function (e) {
    if (e.target.type === 'radio') {
      highlightRow(e.target);
    }
  });

  document.addEventListener('DOMContentLoaded', initRows);
})();
