FROM node:15

WORKDIR /usr/src/app

COPY ./frontend/package.json ./
RUN npm install

COPY ./frontend/compose/local/start-frontend /start-frontend
RUN sed -i 's/\r$//g' /start-frontend
RUN chmod +x /start-frontend

COPY ./ .
EXPOSE 3400

COPY ./frontend/compose/local/start-frontend /start-frontend
RUN sed -i 's/\r$//g' /start-frontend
RUN chmod +x /start-frontend

RUN npm run build

#CMD [ "npm", "run", "start" ]