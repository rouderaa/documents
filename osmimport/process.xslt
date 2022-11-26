<?xml version = "1.0" encoding = "UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                exclude-result-prefixes="i"
>
    <xsl:template match="/">
        <gpx version="1.1" creator="OsmAnd"
        >
            <xsl:text>&#xa;</xsl:text>
            <xsl:for-each select="/gpx/wpt">
                <xsl:sort select="name"/>
                   <xsl:apply-templates select="."/>
                <xsl:text>&#xa;</xsl:text>
            </xsl:for-each>
        </gpx>
    </xsl:template>

    <xsl:template match="/gpx/wpt">
        <wpt>
            <xsl:attribute name="lat">
                <xsl:value-of select="@lat"/>
            </xsl:attribute>
            <xsl:attribute name="lon">
                <xsl:value-of select="@lon"/>
            </xsl:attribute>
            <time>
                <xsl:value-of select="time"/>
            </time>
            <name>
                <xsl:value-of select="name"/>
            </name>
            <extensions>
                <icon><xsl:value-of select="extensions/icon"/></icon>
                <background>circle</background>
                <color><xsl:value-of select="extensions/color"/></color>
                <address>
                    <xsl:value-of select="extensions/address"/>
                </address>
            </extensions>
        </wpt>
    </xsl:template>

</xsl:stylesheet>