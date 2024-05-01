uniform vec2 pos;
uniform float rot;
uniform float radius;

const float PI = 3.14159265359;

void mainImage( out vec4 fragColor, in vec2 fragCoord ) {
    vec2 uv = fragCoord/iResolution.xy;
    vec2 npos = pos;
    float rot = rot;

    float opacity = 0.0;
    vec2 npos_second = vec2(npos.x + radius * cos(rot), npos.y + radius * sin(rot));
    float area = abs(
        fragCoord.y*(npos.x - npos_second.x) 
        + npos.y*(npos_second.x - fragCoord.x) 
        + npos_second.y*(fragCoord.x - npos.x)
    )/2.0;
    float height = area * 2 / distance(npos, npos_second);
    float dot1 = dot(fragCoord, npos);
    float dot2 = dot(fragCoord, npos_second);
    if (dot1 > 0 && dot2 > 0)
        opacity = 1/height;
    fragColor = vec4(vec3(1.0), opacity);
}
