#version 300 es
layout(location = 0) out mediump vec4 outColour;

in mediump vec3 position;
in mediump vec3 normal;
in mediump vec3 colour;
in mediump vec2 uv0;


void main() {
    mediump vec4 ambient = vec4(0.15, 0.15, 0.15, 1);

    vec3 sun = vec3(.2, .3, .5);
    vec3 specular = dot(normal, sun);
    outColour = vec4(specular, 1) + ambient;
}
