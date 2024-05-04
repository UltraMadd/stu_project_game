uniform vec2 pos;
uniform vec3 color;
uniform float radius;

void mainImage( out vec4 fragColor, in vec2 fragCoord )
{
    float dist = distance(fragCoord, pos);

    dist = 1/dist;

    dist *= radius;

    dist = pow(dist, 1.7);

    fragColor = vec4(color, dist);
}
