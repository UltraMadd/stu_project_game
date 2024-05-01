uniform vec2 pos;
uniform vec3 color;
uniform float radius;

void mainImage( out vec4 fragColor, in vec2 fragCoord )
{
    vec2 position = pos;

    float dist = length(fragCoord - position);
    float transparency = 1/(radius - dist);

    fragColor = vec4(color, transparency);
}
