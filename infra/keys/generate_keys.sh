#!/bin/bash

if ! command -v openssl &> /dev/null; then
    echo "Ошибка: OpenSSL не установлен. Установите его и попробуйте снова."
    exit 1
fi

openssl genpkey -algorithm RSA -out private.pem -pkeyopt rsa_keygen_bits:2048

openssl rsa -pubout -in private.pem -out public.pem

chmod 600 private.pem
chmod 644 public.pem

echo "RSA-ключи успешно сохранены в:"
echo "Приватный ключ: private.pem"
echo "Публичный ключ: public.pem"