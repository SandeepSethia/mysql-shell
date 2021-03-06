var mysql = require('mysql');

// The tests assume the next variables have been put in place
// on the JS Context
// __uri: <user>@<host>
// __host: <host>
// __port: <port>
// __user: <user>
// __uripwd: <uri>:<pwd>@<host>
// __pwd: <pwd>

//@ mysql module: exports
var exports = dir(mysql);
print('Exported Items:', exports.length);

print('getClassicSession:', typeof mysql.getClassicSession);
print('help:', typeof mysql.help);

//@ mysql module: getClassicSession through URI
mySession = mysql.getClassicSession(__uripwd);

print(mySession, '\n');

if (mySession.uri == __displayuri)
  print('Session using right URI\n');
else
  print('Session using wrong URI\n');

mySession.close();

//@ mysql module: getClassicSession through URI and password
mySession = mysql.getClassicSession(__uri, __pwd);

print(mySession, '\n');

if (mySession.uri == __displayuri)
  print('Session using right URI\n');
else
  print('Session using wrong URI\n');

mySession.close();

//@ mysql module: getClassicSession through data
var data = {
  host: __host,
  port: __port,
  schema: __schema,
  dbUser: __user,
  dbPassword: __pwd
};

mySession = mysql.getClassicSession(data);

print(mySession, '\n');
print(mySession.uri, '\n');
print(__displayuridb, '\n');

if (mySession.uri == __displayuridb)
  print('Session using right URI\n');
else
  print('Session using wrong URI\n');

mySession.close();

//@ mysql module: getClassicSession through data and password
var data = {
  host: __host,
  port: __port,
  schema: __schema,
  dbUser: __user
};

mySession = mysql.getClassicSession(data, __pwd);

print(mySession, '\n');

if (mySession.uri == __displayuridb)
  print('Session using right URI\n');
else
  print('Session using wrong URI\n');

mySession.close();
