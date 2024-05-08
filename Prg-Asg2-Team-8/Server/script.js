let finish = true;

function clean() {
    document.getElementById("expression").setAttribute('value', '');
    finish = true;
}

function append(x) {
    let expression = document.getElementById("expression").getAttribute('value');
    if(finish) {
        if(x == '.')
            expression = "0" + x;
        else
            expression = x;
    }
    else
        expression += x;
    finish = false;
    document.getElementById("expression").setAttribute('value', expression);
}

function find() {
    let expression = document.getElementById("expression").getAttribute('value');
    document.getElementById("expression").setAttribute('value', String(eval(expression)));
    finish = true;
}

function square() {
    if(finish)
        return;
    let expression = document.getElementById("expression").getAttribute('value');
    document.getElementById("expression").setAttribute('value', String(Math.pow(eval(expression), 2)));
}

function square_root() {
    if(finish)
        return;
    let expression = document.getElementById("expression").getAttribute('value');
    document.getElementById("expression").setAttribute('value', String(Math.pow(eval(expression), 0.5)));
}

function last() {
    let expression = document.getElementById("expression").getAttribute('value');
    document.getElementById("expression").setAttribute('value', expression.slice(0, -1));
}