FROM nginx:alpine

# Remove default nginx configuration
RUN rm /etc/nginx/conf.d/default.conf

# Copy custom nginx configuration
COPY nginx.conf /etc/nginx/conf.d/

# Copy static files
COPY login.html /usr/share/nginx/html/
COPY login.css /usr/share/nginx/html/
COPY login.js /usr/share/nginx/html/
COPY dashboard.html /usr/share/nginx/html/
COPY styles.css /usr/share/nginx/html/
COPY app.js /usr/share/nginx/html/
COPY ticket-management.css /usr/share/nginx/html/
COPY ticket-management.js /usr/share/nginx/html/
COPY notification-system.css /usr/share/nginx/html/
COPY notification-system.js /usr/share/nginx/html/

# Expose port 80
EXPOSE 80

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
