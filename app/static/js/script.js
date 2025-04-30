document.getElementById('borrowDate').value = new Date().toISOString().split('T')[0];
document.getElementById('returnDate').value = new Date().toISOString().split('T')[0];

document.getElementById('reset').addEventListener('submit', function(e) {
    if (!confirm('Are you sure you want to clear all borrowing data?')) {
        e.preventDefault();
    }
});

document.getElementById('borrowForm').addEventListener('submit', function (e) {
    alert('Book borrowed successfully!');
});

document.getElementById('returnForm').addEventListener('submit', function (e) {
    alert('Book returned successfully!');
});