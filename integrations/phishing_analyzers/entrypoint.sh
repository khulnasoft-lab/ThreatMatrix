#!/bin/sh
/usr/bin/sudo /usr/bin/mkdir -p /var/log/threat_matrix/phishing_analyzers
/usr/bin/sudo /usr/bin/touch /var/log/threat_matrix/phishing_analyzers/gunicorn_access.log \
      /var/log/threat_matrix/phishing_analyzers/gunicorn_errors.log
/usr/bin/sudo /usr/bin/chown -R phishing-user:phishing-user \
      /opt/deploy/phishing_analyzers /var/log/threat_matrix/phishing_analyzers

/usr/local/bin/gunicorn 'app:app' \
    --bind '0.0.0.0:4005' \
    --log-level "${LOG_LEVEL}" \
    --user phishing-user \
    --group phishing-user \
    --access-logfile /var/log/threat_matrix/phishing_analyzers/gunicorn_access.log \
    --error-logfile /var/log/threat_matrix/phishing_analyzers/gunicorn_errors.log