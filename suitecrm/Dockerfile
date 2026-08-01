FROM php:8.2-apache-bookworm

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    unzip \
    libpng-dev \
    libjpeg-dev \
    libfreetype6-dev \
    libzip-dev \
    libicu-dev \
    libxml2-dev \
    libc-client-dev \
    libkrb5-dev \
    libldap2-dev \
    libcurl4-openssl-dev \
    libonig-dev \
    && rm -rf /var/lib/apt/lists/*

RUN docker-php-ext-configure gd --with-freetype --with-jpeg \
    && docker-php-ext-configure imap --with-kerberos --with-imap-ssl \
    && docker-php-ext-configure ldap --with-libdir=lib/x86_64-linux-gnu/ \
    && docker-php-ext-install -j$(nproc) \
    gd zip mysqli pdo_mysql intl xml opcache imap soap ldap curl mbstring

# Para evitar el error con la ruta que se muestra nada más acceder al instalador de SuiteCRM
RUN sed -ri \
's!/var/www/html!/var/www/html/public!g' \
/etc/apache2/sites-available/000-default.conf

RUN a2enmod rewrite

# Descargamos el ZIP desde la web oficial, lo descomprimimos y eliminamos el ZIP
WORKDIR /var/www/html
RUN curl -L https://github.com/SuiteCRM/SuiteCRM-Core/releases/download/v8.10.1/SuiteCRM-8.10.1.zip -o suitecrm.zip \
    && unzip suitecrm.zip \
    && rm suitecrm.zip \
    # Mover archivos si se descomprimen en una subcarpeta
    && if [ -d "SuiteCRM-8.10.1" ]; then cp -r SuiteCRM-8.10.1/. .; rm -rf SuiteCRM-8.10.1; fi

# En un entorno de producción estos permisos NO son recomendables.
# Se utilizan únicamente para evitar problemas de permisos durante las prácticas.
RUN mkdir -p /var/www/html/cache \
    /var/www/html/public/legacy/cache \
    /var/www/html/public/legacy/custom \
    /var/www/html/public/legacy/modules \
    /var/www/html/public/legacy/themes \
    /var/www/html/public/legacy/data \
    && chown -R www-data:www-data /var/www/html \
    && chmod -R 755 /var/www/html \
    && chmod -R 777 /var/www/html/cache \
    && chmod -R 777 /var/www/html/public/legacy/cache \
    && chmod -R 777 /var/www/html/public/legacy/custom \
    && chmod -R 777 /var/www/html/public/legacy/modules \
    && chmod -R 777 /var/www/html/public/legacy/themes \
    && chmod -R 777 /var/www/html/public/legacy/data

# Configuración personalizada de PHP para SuiteCRM
RUN echo "memory_limit=512M" > /usr/local/etc/php/conf.d/suitecrm.ini \
    && echo "upload_max_filesize=20M" >> /usr/local/etc/php/conf.d/suitecrm.ini \
    && echo "post_max_size=20M" >> /usr/local/etc/php/conf.d/suitecrm.ini \
    && echo "max_execution_time=300" >> /usr/local/etc/php/conf.d/suitecrm.ini \
    && echo "display_errors=Off" >> /usr/local/etc/php/conf.d/suitecrm.ini \
    && echo "error_reporting=E_ALL & ~E_DEPRECATED & ~E_STRICT & ~E_NOTICE & ~E_WARNING" >> /usr/local/etc/php/conf.d/suitecrm.ini

# Parche para el Route Access Check (fuerza que las comprobaciones dentro del contenedor se hagan contra localhost, sin :8080)
RUN sed -i "s/\$this->checkMainPage();/\$this->checkMainPage('http:\/\/127.0.0.1');/" \
    /var/www/html/core/backend/Install/Service/InstallPreChecks.php \
 && sed -i "s/\$this->checkGraphQlAPI();/\$this->checkGraphQlAPI('http:\/\/127.0.0.1');/" \
    /var/www/html/core/backend/Install/Service/InstallPreChecks.php

# ------------------------------------------------------------------
# Generar automáticamente las claves necesarias para OAuth2.
# Estas claves son necesarias para que funcione la API REST V8
# y la autenticación OAuth2 (FastAPI, n8n, Postman, etc.).
# ------------------------------------------------------------------
RUN mkdir -p /var/www/html/public/legacy/Api/V8/OAuth2 \
    && cd /var/www/html/public/legacy/Api/V8/OAuth2 \
    && openssl genrsa -out private.key 2048 \
    && openssl rsa -in private.key -pubout -out public.key \
    && chmod 600 private.key public.key \
    && chown www-data:www-data private.key public.key

WORKDIR /var/www/html
EXPOSE 80